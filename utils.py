import secrets
import random
import string

def random_password(length: int = 12) -> str:
    """
    Генерирует криптографически стойкий пароль:
    - нижний и верхний регистр
    - цифры
    - набор специальных символов
    """
    alphabet = (
        string.ascii_lowercase +
        string.ascii_uppercase +
        string.digits +
        "!@#$%^&*()-_=+"
    )
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def random_string(length: int = 10) -> str:
    """
    Генерирует случайную строку из строчных букв и цифр.
    Подходит для создания username.
    """
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_credentials(domain: str = "mail.tm") -> tuple[str, str]:
    """
    Возвращает пару (email, password):
    - email: epic<6 случайных символов>@<domain>
    - password: сгенерирован функцией random_password
    """
    username = "epic" + random_string(6)
    email = f"{username}@{domain}"
    password = random_password(12)
    return email, password


# Пример использования
if __name__ == "__main__":
    email, pwd = generate_credentials()
    print("Email:", email)
    print("Password:", pwd)