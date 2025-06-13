from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    image_path = Column(String, nullable=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Связь с объявлениями
    listings = relationship("Listing", backref="user")

    liked_listings = relationship(
        "Listing",
        secondary="listing_likes",
        back_populates="liked_by_users",
        viewonly=True
    )


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    photos = relationship("ListingPhoto", back_populates="listing", cascade="all, delete-orphan")

    # О квартире
    rooms = Column(Integer)
    total_area = Column(Float)
    kitchen_area = Column(Float)
    floor = Column(Integer)
    total_floors = Column(Integer)

    # Условия аренды
    deposit = Column(Integer)
    commission_percent = Column(Float)
    utilities_separate = Column(Boolean, default=True)

    # Правила
    allowed_children = Column(Boolean, default=False)
    allowed_pets = Column(Boolean, default=False)
    allowed_smoking = Column(Boolean, default=False)

    address_city = Column(String)
    address_street = Column(String)
    address_house = Column(String)

    type = Column(String, nullable=False)


    # Описание
    description = Column(Text)

    # Пользователь
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    liked_by_users = relationship(
        "User",
        secondary="listing_likes",
        back_populates="liked_listings",
        viewonly=True
    )


class ListingPhoto(Base):
    __tablename__ = "listing_photos"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id", ondelete="CASCADE"))
    image_path = Column(String, nullable=False)

    listing = relationship("Listing", back_populates="photos")

class Like(Base):
    __tablename__ = "listing_likes"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))