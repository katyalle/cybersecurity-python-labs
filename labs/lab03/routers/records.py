"""Маршрути для записів."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, Response

from labs.lab03 import repository
from labs.lab03.config import VALUE_MAX, VALUE_MIN
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace, Status

router = APIRouter(prefix="/records", tags=["Записи"])

NOT_FOUND = {404: {"description": "Запис або категорію не знайдено"}}
CONFLICT = {409: {"description": "Запис із таким code уже існує"}}


@router.get("", response_model=list[RecordRead], summary="Список записів")
def get_records(
    category_id: int | None = Query(
        default=None, gt=0, description="Лише ця категорія"
    ),
    status: Annotated[Status | None, Query(description="Лише цей статус")] = None,
    min_value: float | None = Query(
        default=None, ge=VALUE_MIN, le=VALUE_MAX, description="value >= min_value"
    ),
    q: str | None = Query(
        default=None, min_length=1, max_length=120, description="Підрядок у title"
    ),
    limit: int = Query(
        default=20, ge=1, le=100, description="Скільки записів повернути"
    ),
    offset: int = Query(default=0, ge=0, description="Скільки записів пропустити"),
):
    """Повернути записи з фільтрами та поділом на сторінки."""
    return repository.list_records(
        category_id=category_id,
        status=status,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/bulk",
    response_model=list[RecordRead],
    status_code=201,
    summary="Пакетне створення записів",
    responses={**NOT_FOUND, **CONFLICT},
)
def post_records_bulk(
    records: Annotated[list[RecordCreate], Body(min_length=1, max_length=100)],
):
    """Створити від 1 до 100 записів: або всі, або жодного."""
    items = [record.model_dump() for record in records]
    try:
        return repository.create_records_bulk(items)
    except repository.CategoryNotFoundError:
        raise HTTPException(status_code=404, detail="Категорію не знайдено")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Запис із таким code уже існує")


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    summary="Один запис",
    responses=NOT_FOUND,
)
def get_record(record_id: int = Path(gt=0, description="Id запису")):
    """Повернути запис за id."""
    try:
        return repository.get_record(record_id)
    except repository.RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Запис не знайдено")


@router.post(
    "",
    response_model=RecordRead,
    status_code=201,
    summary="Створити запис",
    responses={**NOT_FOUND, **CONFLICT},
)
def post_record(record: RecordCreate):
    """Створити новий запис."""
    try:
        return repository.create_record(record.model_dump())
    except repository.CategoryNotFoundError:
        raise HTTPException(status_code=404, detail="Категорію не знайдено")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Запис із таким code уже існує")


@router.put(
    "/{record_id}",
    response_model=RecordRead,
    summary="Повністю замінити запис",
    responses={**NOT_FOUND, **CONFLICT},
)
def put_record(
    record: RecordReplace,
    record_id: int = Path(gt=0, description="Id запису"),
):
    """Замінити всі змінювані поля запису; id лишається тим самим."""
    try:
        return repository.replace_record(record_id, record.model_dump())
    except (repository.RecordNotFoundError, repository.CategoryNotFoundError):
        raise HTTPException(status_code=404, detail="Запис або категорію не знайдено")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Запис із таким code уже існує")


@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Видалити запис",
    responses=NOT_FOUND,
)
def remove_record(record_id: int = Path(gt=0, description="Id запису")):
    """Видалити запис за id."""
    try:
        repository.delete_record(record_id)
    except repository.RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    return Response(status_code=204)
