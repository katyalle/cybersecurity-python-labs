"""Завдання 1: Комплексний аналізатор надійності паролів (Варіант 15)."""

import random
import string
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER  # noqa: E402

passwords = [
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

criteria = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

forbidden_passwords = {
    "standard",
    "typical123",
    "normal",
    "general123",
    "common",
    "guest",
}


def analyze_passwords() -> None:
    """Оцінює стійкість паролів до компрометації."""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n")

    working_passwords = passwords.copy()
    random_indices = random.sample(range(len(working_passwords)), 3)
    duplicates = [working_passwords[i] for i in random_indices]
    working_passwords.extend(duplicates)

    min_len = criteria["min_length"]
    special_chars = set(string.punctuation)

    results = []

    for pwd in working_passwords:
        has_digit = any(char.isdigit() for char in pwd)
        has_upper = any(char.isupper() for char in pwd)
        has_lower = any(char.islower() for char in pwd)
        has_special = any(char in special_chars for char in pwd)

        all_criteria_met = (
            len(pwd) >= min_len and has_digit and has_upper and has_lower and has_special
        )
        is_forbidden = pwd in forbidden_passwords or len(pwd) < min_len
        is_unique = working_passwords.count(pwd) == 1

        if is_forbidden:
            category = "Заборонений"
        elif all_criteria_met:
            if len(pwd) >= min_len + 4 and is_unique:
                category = "Дуже сильний"
            else:
                category = "Сильний"
        elif len(pwd) >= min_len and sum([has_digit, has_upper, has_lower, has_special]) >= 2:
            category = "Середній"
        else:
            category = "Слабкий"

        results.append((pwd, category))

    print(f"{'№':<4} | {'Пароль':<22} | {'Категорія надійності'}")
    print("-" * 52)
    for idx, (pwd, category) in enumerate(results, 1):
        print(f"{idx:<4} | {pwd:<22} | {category}")


if __name__ == "__main__":
    analyze_passwords()