import os
import random
import string
import sys

# Додаємо кореневу папку проєкту у шляхи пошуку модулів
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

PASSWORDS = [
    "IoT@S3curity",
    "standard",
    "Blockchain@Protect",
    "typical123",
    "AI@Cybersec",
    "normal",
    "Quantum@Crypto",
    "general123",
    "Edge@S3curity",
    "common",
]

CRITERIA = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

FORBIDDEN_PASSWORDS = {
    "standard",
    "typical123",
    "normal",
    "general123",
    "common",
    "guest",
}


def evaluate_password(password: str, all_passwords: list) -> str:
    """Оцінює надійність одного пароля за критеріями варіанта 15."""
    if password in FORBIDDEN_PASSWORDS or len(password) < CRITERIA["min_length"]:
        return "Заборонений / Слабкий"

    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_special = any(c in string.punctuation for c in password)

    meets_all = has_digit and has_upper and has_lower and has_special
    is_unique = all_passwords.count(password) == 1

    if meets_all:
        if len(password) >= CRITERIA["min_length"] + 4 and is_unique:
            return "Дуже сильний"
        return "Сильний"

    matches = sum([has_digit, has_upper, has_lower, has_special])
    if matches >= 2:
        return "Середній"

    return "Слабкий"


def analyze_passwords():
    """Головна функція для завдання 1."""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n")

    working_passwords = PASSWORDS.copy()

    random.seed(42)
    random_indices = random.sample(range(len(working_passwords)), 3)
    duplicates = [working_passwords[i] for i in random_indices]
    working_passwords.extend(duplicates)

    print(f"{'№':<3} | {'Пароль':<22} | {'Оцінка надійності'}")
    print("-" * 55)
    for idx, pwd in enumerate(working_passwords, start=1):
        status = evaluate_password(pwd, working_passwords)
        print(f"{idx:<3} | {pwd:<22} | {status}")


if __name__ == "__main__":
    analyze_passwords()