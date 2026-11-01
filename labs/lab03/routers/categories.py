"""Маршрути для категорій."""

import sqlite3

from fastapi import APIRouter, HTTPException, Path, Response

from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Категорії"])


@router.get("", response_model=list[CategoryRead], summary="Список категорій")
def get_categories():
    """Повернути всі категорії за зростанням id."""
    return repository.list_categories()


@router.post(
    "",
    response_model=CategoryRead,
    status_code=201,
    summary="Створити категорію",
    responses={409: {"description": "Категорія з такою назвою вже існує"}},
)
def post_category(category: CategoryCreate):
    """Створити нову категорію."""
    try:
        return repository.create_category(category.name)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409, detail="Категорія з такою назвою вже існує"
        )


@router.delete(
    "/{category_id}",
    status_code=204,
    summary="Видалити порожню категорію",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Категорія містить записи"},
    },
)
def remove_category(category_id: int = Path(gt=0, description="Id категорії")):
    """Видалити категорію, якщо в ній немає записів."""
    try:
        repository.delete_category(category_id)
    except repository.CategoryNotFoundError:
        raise HTTPException(status_code=404, detail="Категорію не знайдено")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Категорія містить записи")
    return Response(status_code=204)
