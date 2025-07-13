
# main.py
import asyncio
from tempmail import create_account_async, wait_for_confirmation_async, extract_epic_confirmation_link
from register import register_epic_account
from confirm import confirm_email_by_browser
import db

async def handle_account() -> None:
    """Полный цикл создания и подтверждения одного аккаунта."""
    try:
        # 1. Создаём временную почту
        acc = await create_account_async()
        email = acc["email"]
        password = acc["password"]
        token = acc["token"]
        print(f"📧 Используем temp-mail: {email}")

        # 2. Регистрируем аккаунт на Epic Games
        await register_epic_account(email=email, password=password)
        print(f"🔐 Успешно зарегистрированы: {email}")

        # 3. Ожидаем письмо с подтверждением
        print(f"⏳ Ждём письмо подтверждения на {email}...")
        msg = await wait_for_confirmation_async(token, timeout=90)
        if not msg:
            print(f"❌ Письмо не пришло для {email}")
            return

        # 4. Извлекаем ссылку и подтверждаем
        link = extract_epic_confirmation_link(msg)
        if not link:
            print(f"❌ Ссылка подтверждения не найдена в письме для {email}")
            return
        print(f"🔗 Ссылка подтверждения: {link}")
        confirm_email_by_browser(link)
        print(f"✅ Аккаунт подтверждён: {email}")

        # 5. Сохраняем данные в БД
        db.insert_account(email=email, password=password)
        print(f"💾 Сохранено в БД: {email}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def main() -> None:
    """Последовательно обрабатываем заданное количество аккаунтов."""
    count = 1  # устанавливаем 1 для открытия только одного окна браузера
    for _ in range(count):
        await handle_account()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
