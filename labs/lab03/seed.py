import json
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

SEED_PATH = Path(__file__).resolve().parent / "data" / "seed.json"


def load_seed() -> dict:
    """Прочитати й перевірити структуру початкових даних."""
    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    if not isinstance(data.get("categories"), list) or not isinstance(
        data.get("records"), list
    ):
        raise TypeError("seed.json має містити масиви categories і records")
    if len(data["categories"]) != 3 or len(data["records"]) != 8:
        raise ValueError("Очікується 3 категорії та 8 записів")
    return data


def database_is_empty(connection: sqlite3.Connection) -> bool:
    """Перевірити, що в обох таблицях немає рядків."""
    categories = connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    records = connection.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    return categories == 0 and records == 0


def seed_database() -> None:
    """Заповнити порожню базу початковими даними в одній транзакції."""
    try:
        data = load_seed()
    except (OSError, TypeError, ValueError) as error:
        print(f"Некоректні початкові дані: {error}")
        return

    initialize_database()
    with closing(get_connection()) as connection:
        if not database_is_empty(connection):
            print("База вже містить дані, заповнення пропущено.")
            return
        try:
            with connection:
                connection.executemany(
                    "INSERT INTO categories (id, name) VALUES (:id, :name)",
                    data["categories"],
                )
                connection.executemany(
                    "INSERT INTO records (code, title, category_id, value, status) "
                    "VALUES (:code, :title, :category_id, :value, :status)",
                    data["records"],
                )
        except (sqlite3.Error, KeyError) as error:
            print(f"Заповнення скасовано, зміни не збережено: {error}")
            return
    print("Додано 3 категорії та 8 записів.")


if __name__ == "__main__":
    seed_database()
