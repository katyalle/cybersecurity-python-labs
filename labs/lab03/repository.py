"""Параметризовані SQL-запити до бази. Не залежить від FastAPI."""

import sqlite3
from contextlib import closing
from typing import Any

from labs.lab03.database import get_connection


class RecordNotFoundError(Exception):
    """Запис із таким id не існує."""


class CategoryNotFoundError(Exception):
    """Категорія з таким id не існує."""


RECORD_SELECT = """
    SELECT r.id, r.code, r.title, r.category_id,
           c.name AS category_name, r.value, r.status
    FROM records AS r
    JOIN categories AS c ON c.id = r.category_id
"""


def _open() -> sqlite3.Connection:
    """Відкрити з'єднання, щоб рядки читалися за іменами стовпців."""
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_category(connection: sqlite3.Connection, category_id: int) -> None:
    """Перевірити, що категорія існує."""
    row = connection.execute(
        "SELECT id FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    if row is None:
        raise CategoryNotFoundError


def _get_record(connection: sqlite3.Connection, record_id: int) -> dict[str, Any]:
    """Прочитати один запис разом з назвою категорії."""
    row = connection.execute(RECORD_SELECT + " WHERE r.id = ?", (record_id,)).fetchone()
    if row is None:
        raise RecordNotFoundError
    return dict(row)


# ---------- Категорії ----------


def create_category(name: str) -> dict[str, Any]:
    """Створити категорію."""
    with closing(_open()) as connection:
        with connection:
            cursor = connection.execute(
                "INSERT INTO categories (name) VALUES (?)", (name,)
            )
        return {"id": cursor.lastrowid, "name": name}


def list_categories() -> list[dict[str, Any]]:
    """Список категорій за зростанням id."""
    with closing(_open()) as connection:
        rows = connection.execute(
            "SELECT id, name FROM categories ORDER BY id ASC"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_category(category_id: int) -> None:
    """Видалити категорію (якщо вона порожня)."""
    with closing(_open()) as connection, connection:
        cursor = connection.execute(
            "DELETE FROM categories WHERE id = ?", (category_id,)
        )
        if cursor.rowcount == 0:
            raise CategoryNotFoundError


# ---------- Записи ----------


def create_record(data: dict[str, Any]) -> dict[str, Any]:
    """Додати запис і повернути його з category_name."""
    with closing(_open()) as connection:
        with connection:
            _ensure_category(connection, data["category_id"])
            cursor = connection.execute(
                "INSERT INTO records (code, title, category_id, value, status) "
                "VALUES (:code, :title, :category_id, :value, :status)",
                data,
            )
            record_id = cursor.lastrowid
        return _get_record(connection, record_id)


def get_record(record_id: int) -> dict[str, Any]:
    """Отримати запис за id."""
    with closing(_open()) as connection:
        return _get_record(connection, record_id)


def list_records(
    *,
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Список записів із фільтрами та поділом на сторінки."""
    conditions: list[str] = []
    params: list[Any] = []

    if category_id is not None:
        conditions.append("r.category_id = ?")
        params.append(category_id)
    if status is not None:
        conditions.append("r.status = ?")
        params.append(status)
    if min_value is not None:
        conditions.append("r.value >= ?")
        params.append(min_value)
    if q is not None:
        conditions.append("instr(r.title, ?) > 0")
        params.append(q)

    sql = RECORD_SELECT
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(_open()) as connection:
        rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def replace_record(record_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """Повністю замінити змінювані поля запису; id не змінюється."""
    with closing(_open()) as connection:
        with connection:
            _get_record(connection, record_id)
            _ensure_category(connection, data["category_id"])
            connection.execute(
                "UPDATE records SET code = :code, title = :title, "
                "category_id = :category_id, value = :value, status = :status "
                "WHERE id = :id",
                {**data, "id": record_id},
            )
        return _get_record(connection, record_id)


def delete_record(record_id: int) -> None:
    """Видалити запис."""
    with closing(_open()) as connection, connection:
        cursor = connection.execute("DELETE FROM records WHERE id = ?", (record_id,))
        if cursor.rowcount == 0:
            raise RecordNotFoundError


def create_records_bulk(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Додати пакет записів в одній транзакції (все або нічого)."""
    with closing(_open()) as connection:
        with connection:
            ids: list[int] = []
            for data in items:
                _ensure_category(connection, data["category_id"])
                cursor = connection.execute(
                    "INSERT INTO records (code, title, category_id, value, status) "
                    "VALUES (:code, :title, :category_id, :value, :status)",
                    data,
                )
                ids.append(cursor.lastrowid)
        return [_get_record(connection, record_id) for record_id in ids]
