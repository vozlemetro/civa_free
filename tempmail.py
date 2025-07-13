
import asyncio
import httpx
import uuid
import random
from utils import random_password
API_BASE = "https://api.mail.tm"


# New helper to get a random domain
async def get_random_domain():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/domains")
        data = resp.json()
        domains = [d["domain"] for d in data["hydra:member"]]
        return random.choice(domains)

async def create_account_async():
    # Генерируем уникальные учётные данные
    domain = await get_random_domain()
    name = f"epic_{uuid.uuid4().hex[:8]}"
    email = f"{name}@{domain}"
    password = random_password(12)

    async with httpx.AsyncClient() as client:
        # 1) Создание почты
        resp = await client.post(
            f"{API_BASE}/accounts",
            json={"address": email, "password": password}
        )
        if resp.status_code != 201:
            raise Exception(f"Ошибка при создании почты: [{resp.status_code}] {resp.text}")

        # 2) Получение токена
        token_resp = await client.post(
            f"{API_BASE}/token",
            json={"address": email, "password": password}
        )
        if token_resp.status_code != 200:
            raise Exception("Ошибка авторизации", token_resp.text)
        token = token_resp.json()["token"]

    return {"email": email, "password": password, "token": token}


async def wait_for_confirmation_async(token: str, timeout: int = 60):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        for _ in range(timeout):
            r = await client.get(f"{API_BASE}/messages", headers=headers)
            msgs = r.json().get("hydra:member", [])
            if msgs:
                return msgs[0]
            await asyncio.sleep(1)
    return None

def extract_epic_confirmation_link(message: dict) -> str | None:
    """
    Извлекает ссылку на подтверждение Epic из тела письма.
    Обычно Epic шлёт письмо с ссылкой вида:
    https://www.epicgames.com/id/verify/email?token=...

    Мы ищем первую такую ссылку.
    """
    # Вариант 1: из plain text
    if "text" in message:
        lines = message["text"].splitlines()
        for line in lines:
            if "https://" in line and "verify" in line:
                return line.strip()

    # Вариант 2: из html (если текст не дал ссылку)
    if "html" in message:
        import re
        links = re.findall(r'https://[^\s"\']+', message["html"])
        for link in links:
            if "verify" in link:
                return link

    return None