from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__="user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorite_characters: Mapped[list["FavoriteCharacter"]] = relationship(back_populates="user")
    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorite_characters": [fav.serialize() for fav in self.favorite_characters],
            "favorite_planets": [fav.serialize() for fav in self.favorite_planets]
        }

class Character(db.Model):
    __tablename__="character"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    hair_color: Mapped[str] = mapped_column(nullable=False)
    eye_color: Mapped[str] = mapped_column(nullable=False)

    favorited_by: Mapped[list["FavoriteCharacter"]] = relationship(back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
        }
    

class FavoriteCharacter(db.Model):
    __tablename__="favorite_character"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorite_characters")
    character: Mapped["Character"] = relationship(back_populates="favorited_by")

    def serialize(self):
        return {
            "id": self.id,
            "character": self.character.serialize()
        }
    

class Planet(db.Model):
    __tablename__="planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    diameter: Mapped[str] = mapped_column(nullable=False)
    terrain: Mapped[str] = mapped_column(nullable=False)
    
    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship(back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "terrain": self.terrain,
        }
    

class FavoritePlanet(db.Model):
    __tablename__="favorite_planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorite_planets")
    planet: Mapped["Planet"] = relationship(back_populates="favorite_planets")

    def serialize(self):
        return {
            "id": self.id,
            "planet": self.planet.serialize()
        }