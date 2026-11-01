"""FastAPI-застосунок для лабораторної роботи №3 (варіант 15)."""

import logging
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from labs.lab03.config import DOMAIN_DESCRIPTION, DOMAIN_TITLE, UNIT
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared import student

logger = logging.getLogger("lab03")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Під час запуску створити відсутні таблиці (дані не чіпаємо)."""
    initialize_database()
    yield


app = FastAPI(
    title=DOMAIN_TITLE,
    description=f"{DOMAIN_DESCRIPTION} Одиниця вимірювання value: {UNIT}.",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.exception_handler(sqlite3.OperationalError)
async def handle_database_error(request: Request, error: sqlite3.OperationalError):
    """Технічну помилку бази записати в лог, клієнту дати просте повідомлення."""
    logger.error("Помилка бази даних: %s", error)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутрішня помилка сервера"},
    )


@app.get("/ping", summary="Перевірка доступності API")
def ping():
    """Повернути ok, якщо сервер працює."""
    return {"status": "ok"}


@app.get("/student", summary="Дані студента")
def get_student():
    """Повернути ПІБ, групу та номер варіанта."""
    return {
        "student_name": student.STUDENT_NAME,  # <-- ТУТ
        "group_name": student.GROUP_NAME,  # <-- ТУТ
        "variant_number": student.VARIANT_NUMBER,  # <-- ТУТ
    }
