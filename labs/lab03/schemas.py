"""Pydantic-моделі запитів і відповідей."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from labs.lab03.config import VALUE_MAX, VALUE_MIN

Status = Literal["new", "in_progress", "done"]


class CategoryCreate(BaseModel):
    """Тіло запиту для створення категорії."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=40)


class CategoryRead(BaseModel):
    """Категорія у відповіді."""

    id: int
    name: str


class RecordCreate(BaseModel):
    """Тіло запиту для створення запису."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    code: str = Field(min_length=3, max_length=40)
    title: str = Field(min_length=3, max_length=120)
    category_id: int = Field(gt=0)
    value: float = Field(ge=VALUE_MIN, le=VALUE_MAX, allow_inf_nan=False)
    status: Status


class RecordReplace(RecordCreate):
    """Тіло PUT: усі змінювані поля обов'язкові."""


class RecordRead(RecordCreate):
    """Запис у відповіді: змінювані поля + id і назва категорії."""

    id: int
    category_name: str
