from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "user_name": self.user_name
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    population: Mapped[int] = mapped_column(nullable=True, default=0)
    climate: Mapped[str] = mapped_column(String(100), nullable=True)

    favorited_by: Mapped[list["Favorite"]] = relationship(
        back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "climate": self.climate
        }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)

    favorited_by: Mapped[list["Favorite"]] = relationship(
        back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "description": self.description
        }


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey('user.id'), nullable=False)
    planet_id: Mapped[int] = mapped_column(
        db.ForeignKey('planet.id'), nullable=True)
    character_id: Mapped[int] = mapped_column(
        db.ForeignKey('character.id'), nullable=True)

    user: Mapped["User"] = relationship(back_populates="favorites")
    planet: Mapped["Planet"] = relationship(back_populates="favorited_by")
    character: Mapped["Character"] = relationship(
        back_populates="favorited_by")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id
        }
