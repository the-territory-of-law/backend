"""Общий DeclarativeBase для ORM-модулей (единая metadata для create_all / Alembic)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
