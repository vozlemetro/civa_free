from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, random

from utils import random_string, random_password

def register_epic_account(email: str, password: str, proxy: str = None):
    """
    Регистрирует аккаунт Epic Games через selenium.
    """
    # Настройка Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={generate_user_agent()}")

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://www.epicgames.com/id/register")
        time.sleep(random.uniform(3, 5))  # Ждём полной загрузки

        # Выбираем страну (оставим по умолчанию, если уже стоит)

        # Имя и фамилия
        name = random_string(6)
        surname = random_string(7)
        driver.find_element(By.NAME, "name").send_keys(name)
        driver.find_element(By.NAME, "lastName").send_keys(surname)

        # Email
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "displayName").send_keys(name + random_string(4))

        # Согласие с условиями
        driver.find_element(By.CLASS_NAME, "css-checkbox").click()

        # Нажимаем кнопку зарегистрироваться
        submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
        submit.click()

        # Ждём либо капчу, либо редирект
        time.sleep(5)

        # Проверка успешной регистрации — смотрим URL или заголовок
        if "verify" in driver.current_url:
            print(f"Аккаунт {email} создан, ожидает подтверждения.")
        else:
            print(f"Аккаунт {email} возможно уже зарегистрирован или капча.")

    except Exception as e:
        print(f"Ошибка при регистрации: {e}")

    finally:
        driver.quit()

def generate_user_agent():
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/14.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Gecko/20100101 Firefox/90.0",
    ]
    return random.choice(ua_list)

# Пример:
# register_epic_account("epic_xyz@mail.tm", "StrongPass123!", proxy="http://user:pass@ip:port")