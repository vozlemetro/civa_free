# confirm.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def confirm_email_by_browser(link: str):
    """
    Открывает ссылку подтверждения в headless-режиме.
    Эмулирует поведение пользователя.
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--log-level=3')  # тише лог
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    time.sleep(5)  # ждём прогрузку
    driver.quit()