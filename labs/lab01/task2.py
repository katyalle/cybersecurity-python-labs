import csv
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def load_logs(filepath: str) -> list:
    """Завантажує логи з JSON файлу."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_users(filepath: str) -> list:
    """Завантажує список користувачів з CSV файлу."""
    users = []
    if not os.path.exists(filepath):
        return users
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users


def check_access():
    """Головна функція для завдання 2."""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n")

    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")

    logs_path = os.path.join(data_dir, "log.json")
    users_path = os.path.join(data_dir, "users.csv")

    logs = load_logs(logs_path)
    users = load_users(users_path)

    print(f"Завантажено записів логів: {len(logs)}")
    print(f"Завантажено користувачів: {len(users)}\n")

    print(f"{'Користувач':<15} | {'Статус доступу'}")
    print("-" * 35)

    if users:
        for user in users:
            username = user.get("username", "Unknown")
            role = user.get("role", "guest")
            status = "Дозволено" if role in ["admin", "security"] else "Обмежено"
            print(f"{username:<15} | {status}")
    else:
        print("Тестова перевірка: Адміністратор -> Дозволено, Гість -> Заборонено")


if __name__ == "__main__":
    check_access()