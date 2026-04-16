"""Shared schema building blocks."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def build(cls, *, page: int, page_size: int, total: int) -> PageMeta:
        total_pages = (total + page_size - 1) // page_size if page_size else 0
        return cls(page=page, page_size=page_size, total=total, total_pages=total_pages)


class Page(BaseModel, Generic[T]):
    items: list[T] = Field(default_factory=list)
    meta: PageMeta


class HealthStatus(BaseModel):
    status: str
    app: str
    version: str
    env: str
    database: str
    now: str
