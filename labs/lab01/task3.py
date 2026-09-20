"""Завдання 3: Хешування, CSV-база та JSON-логування з винятками (Варіант 15)."""

import csv
import functools
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared.student import VARIANT_NUMBER  # noqa: E402


class ValidationError(Exception):
    """Виняток для помилок валідації пароля."""

    pass


HASH_ALGORITHM = "sha1"
MIN_PASSWORD_LEN = 9
DATA_DIR = Path(__file__).resolve().parent / "data"
CSV_FILE = DATA_DIR / "users.csv"
LOG_FILE = DATA_DIR / "log.json"


def generate_salt() -> str:
    """Генерує сіль у форматі 5 символів."""
    return f"{VARIANT_NUMBER:05d}"


SALT = generate_salt()


def generate_hash(password: str, salt: str = "00000") -> str:
    """Генерує SHA-1 хеш пароля із сіллю."""
    if not password or not salt:
        raise ValueError("Пароль та сіль не можуть бути порожніми!")

    if len(password) < MIN_PASSWORD_LEN:
        raise ValidationError(
            f"Пароль закороткий! Мінімальна довжина: {MIN_PASSWORD_LEN}"
        )

    salted = password + salt
    return hashlib.sha1(salted.encode("utf-8")).hexdigest()


def log_event(func):
    """Декоратор для автоматичного логування спроб авторизації у JSON."""

    @functools.wraps(func)
    def wrapper(username: str, password: str, *args, **kwargs):
        result = func(username, password, *args, **kwargs)

        event_data = {
            "event": "login",
            "user": username,
            "result": "success" if result else "failure",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        logs = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        logs.append(event_data)

        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)

        return result

    return wrapper


def create_user(username: str, password: str) -> tuple[str, str]:
    """Створює пару (логін, хеш)."""
    return username, generate_hash(password, SALT)


def create_users(users_list: list[tuple[str, str]]) -> None:
    """Зберігає список користувачів у CSV-файл."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    prepared_users = []
    for user, pwd in users_list:
        try:
            prepared_users.append(create_user(user, pwd))
        except (ValueError, ValidationError) as e:
            print(f"Помилка створення користувача {user}: {e}")

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password_hash"])
        writer.writerows(prepared_users)


def read_users_db() -> list[tuple[str, str]]:
    """Зчитує користувачів із CSV-файлу."""
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"Файл {CSV_FILE} не знайдено!")

    users_db = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                users_db.append((row[0], row[1]))
    return users_db


@log_event
def login(username: str, password: str) -> bool:
    """Спроба входу користувача."""
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми!")

    users_db = read_users_db()

    try:
        current_hash = generate_hash(password, SALT)
    except ValidationError:
        return False

    for db_user, db_hash in users_db:
        if db_user == username and db_hash == current_hash:
            return True

    return False


def main() -> None:
    """Головна функція Завдання 3."""
    users_to_register = [
        ("user1", "QuantumSecure123"),
        ("user2", "SuperPassword1!"),
        ("user3", "ShortPass"),
        ("user4", "CryptoNode2026"),
        ("user5", "PostQuantumKey99"),
        ("user6", "SecureNetwork77"),
        ("user7", "IoT_Device_Pass1"),
        ("user8", "BlockchainPass#1"),
        ("user9", "CyberSecurity#15"),
        ("user10", "FinalPassword!"),
    ]

    try:
        print("--- Створення CSV-бази користувачів ---")
        create_users(users_to_register)

        print("\n--- Зчитаний вміст users.csv ---")
        users_db = read_users_db()
        for user, pwd_hash in users_db:
            print(f"{user:<12} | {pwd_hash}")

        print("\n--- Спроби входу (логування у JSON) ---")
        test_logins = [
            ("user1", "QuantumSecure123"),
            ("user2", "WrongPass123"),
            ("user3", "ShortPass"),
        ]

        for u, p in test_logins:
            status = "УСПІШНО" if login(u, p) else "ВІДМОВЛЕНО"
            print(f"Спроба входу user=[{u}] -> {status}")

    except (FileNotFoundError, IOError) as file_err:
        print(f"Помилка файлової системи: {file_err}")
    except (ValidationError, ValueError) as val_err:
        print(f"Помилка валідації: {val_err}")


if __name__ == "__main__":
    main()