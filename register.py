# register.py – Epic Games регистрация с корректным вводом e-mail (июль-2025)

import random
import asyncio
import re
import traceback
import uuid
from playwright.async_api import async_playwright, Browser
from faker import Faker

faker = Faker()
REGISTER_URL = "https://www.epicgames.com/id/register/date-of-birth?lang=ru"


async def cookie_guard(page):
    """Закрывает возможный cookie-баннер."""
    for txt in ("Принять", "Accept"):
        btn = page.locator(f"button:has-text('{txt}')")
        if await btn.is_visible():
            await btn.click()
            break


async def pick_from_combobox(frame, label_ru, val):
    """Выбирает из combobox «День» или «Месяц»."""
    btn = frame.get_by_role("combobox", name=label_ru)
    await btn.click()
    month_map = ["янв","фев","мар","апр","май","июн",
                 "июл","авг","сен","окт","ноя","дек"]
    target = month_map[int(val)-1] if label_ru == "Месяц" else val
    opt = frame.get_by_role("option", name=re.compile(rf"^{re.escape(target)}$", re.I))
    if await opt.count():
        await opt.click()
    else:
        await frame.get_by_role("option").nth(int(val)-1).click()


async def find_frame_with_selector(page, css_list, timeout=15_000):
    """
    Ищет iframe или root, где есть любой селектор из css_list.
    """
    await page.wait_for_load_state("domcontentloaded")
    await cookie_guard(page)
    for _ in range(timeout // 500):
        # проверяем корневой фрейм
        for css in css_list:
            if await page.query_selector(css):
                return page.main_frame
        # проверяем вложенные iframe
        for fr in page.frames:
            for css in css_list:
                if await fr.query_selector(css):
                    return fr
        await asyncio.sleep(0.5)
    raise RuntimeError(f"Не найден фрейм для селекторов: {css_list}")


async def register_epic_account(email: str, password: str) -> None:
    print(f"\n🚀 Старт регистрации: {email}")
    browser: Browser | None = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(locale="ru-RU")
            page = await context.new_page()

            # 1) Дата рождения
            await page.goto(REGISTER_URL, wait_until="domcontentloaded")
            dob_frame = await find_frame_with_selector(
                page, ["input[placeholder='Год']", "select[name='day']"]
            )
            year      = str(random.randint(1993, 2005))
            month_num = str(random.randint(1, 12))
            day_num   = str(random.randint(1, 28))
            await pick_from_combobox(dob_frame, "День",  day_num)
            await pick_from_combobox(dob_frame, "Месяц", month_num)
            await dob_frame.fill("input[placeholder='Год']", year)
            print(f"📅 ДР: {day_num}.{month_num}.{year}")
            await dob_frame.get_by_role(
                "button", name=re.compile("Продолжить|Continue", re.I)
            ).click()

            # 2) Форма учётной записи
            await page.wait_for_url(re.compile(r"/register\?lang="), timeout=15_000)
            reg_frame = await find_frame_with_selector(
                page, ["input[name='email']:visible", "input[name='displayName']"]
            )

            # ==== ввод e-mail из tempmail с проверкой ====
            print(f"🔧 DEBUG: вводим {email} в форму")
            email_input = reg_frame.locator("input[name='email']:visible").first
            await email_input.click()
            await email_input.fill("")                   # очищаем
            await email_input.type(email, delay=70)      # «ручной» ввод
            await email_input.press("Tab")               # триггерим blur
            await page.wait_for_timeout(1000)            # ждём JS-валидацию

            # если Epic подчистил или отклонил e-mail
            current = await email_input.input_value()
            if current != email:
                raise RuntimeError(f"Epic перезаписал email → «{current}»")

            # ==== остальные поля ====
            first = faker.first_name()
            last  = faker.last_name()
            display_name = f"{first.lower()}.{last.lower()}{uuid.uuid4().hex[:6]}"
            print(f"Используем displayName: {display_name}")

            await reg_frame.fill("input[name='name'], input[name='firstName']", first)
            await reg_frame.fill("input[name='familyName'], input[name='lastName']", last)
            await reg_frame.fill("input[name='displayName']", display_name)
            await reg_frame.fill("input[name='password']",    password)

            # случайный выбор страны
            country_btn = reg_frame.get_by_role("combobox", name=re.compile("Страна", re.I))
            if await country_btn.count():
                await country_btn.click()
                country_opt = reg_frame.get_by_role(
                    "option", name=re.compile(re.escape(faker.country()), re.I)
                )
                if await country_opt.count():
                    await country_opt.click()
                else:
                    await reg_frame.get_by_role("option").first.click()

            # Terms of Service
            tos = reg_frame.get_by_label("Я прочитал(-а) и принимаю Условия обслуживания")
            if await tos.count():
                await tos.check()
            else:
                inp = reg_frame.locator("input[name='termsOfService']")
                await inp.scroll_into_view_if_needed()
                await inp.check(force=True)

            print("✍️ Анкета заполнена")

            # 3) Отправляем форму и ждём подтверждения
            await reg_frame.locator(
                "button[type='submit'], button:has-text('Продолжить')"
            ).first.click()

            await page.wait_for_selector(
                "text=/Проверьте адрес|Check your email/", timeout=25_000
            )
            print("✅ Учётка создана, письмо отправлено")

            await context.close()
            await browser.close()

    except Exception:
        print("❌ Ошибка регистрации:")
        traceback.print_exc()
        if browser:
            await browser.close()
        # прокидываем наверх, чтобы main.py создал новый email
        raise