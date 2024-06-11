"""Module that provides models."""
import uuid
from typing import List

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

NAME_LENGTH = 100


class Base(DeclarativeBase):
    """Base class."""

    pass


def serialize_decorator(cls: type) -> type:
    """Provide method for serialize json.

    Args:
        cls (type): class for decorate.

    Returns:
        type: decorated class.
    """
    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    setattr(cls, 'as_dict', as_dict)
    return cls


class IDNameMixin:
    """Mixin that provide id and name."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=False)


@serialize_decorator
class Character(IDNameMixin, Base):
    """Represents charater.

    Args:
        IDNameMixin (_type_): _description_
        Base (_type_): _description_
    """

    __tablename__ = 'character'
    class_name: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=False)
    race_name: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=False)
    health: Mapped[int] = mapped_column(Integer(), nullable=False)
    damage: Mapped[int] = mapped_column(Integer(), nullable=False)
    spell_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('spell.id'), nullable=True)
    spell: Mapped['Spell'] = relationship(
        back_populates='characters',
    )
    __table_args__ = (
        UniqueConstraint('name', 'class_name', 'race_name', name='name_class_race_unique'),
    )


@serialize_decorator
class Spell(IDNameMixin, Base):
    """Represent character spell.

    Args:
        IDNameMixin (_type_): _description_
        Base (_type_): _description_
    """

    __tablename__ = 'spell'
    aspect: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=False)
    damage: Mapped[int] = mapped_column(Integer())

    characters: Mapped[List['Character']] = relationship(
        back_populates='spell', cascade='all, delete-orphan',
    )
    __table_args__ = (UniqueConstraint('name', 'aspect', name='name_apsect_unique'),)
