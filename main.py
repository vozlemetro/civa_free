import asyncio
from tempmail import create_account_async, wait_for_confirmation_async, extract_epic_confirmation_link
from confirm import confirm_email_by_browser
from register import register_epic_account
import db

async def handle_account():
    # 1. Создание почты
    acc = await create_account_async()
    email, password, token = acc["email"], acc["password"], acc["token"]

    # 2. Регистрация на Epic Games
    register_epic_account(email=email, password=password)

    # 3. Ожидание письма
    print(f"Ждём письмо на {email}...")
    msg = await wait_for_confirmation_async(token, timeout=90)
    if not msg:
        print(f"❌ Письмо не пришло для {email}")
        return

    # 4. Извлечение ссылки и подтверждение
    link = extract_epic_confirmation_link(msg)
    if link:
        confirm_email_by_browser(link)
        print(f"✅ {email} подтверждён.")
    else:
        print(f"❌ Ссылка не найдена в письме для {email}")
        return

    # 5. Сохранение в базу
    db.insert_account(email=email, password=password)
    print(f"💾 Сохранили аккаунт {email}")

async def main():
    tasks = [handle_account() for _ in range(5)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())