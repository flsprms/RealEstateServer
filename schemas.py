from datetime import datetime

from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ListingPreview(BaseModel):
    id: int
    title: str
    price: int
    owner_name: str
    image_base64: str | None
    liked_by_users: list[int] = []

class ListingBase(BaseModel):
    title: str
    price: int

    # О квартире
    rooms: int
    total_area: float
    kitchen_area: float
    floor: int
    total_floors: int

    # Условия аренды
    deposit: int
    commission_percent: float
    utilities_separate: bool = True

    # Правила
    allowed_children: bool = False
    allowed_pets: bool = False
    allowed_smoking: bool = False

    address_city: str
    address_street: str
    address_house: str

    type: str

    # Описание
    description: str

    # Фото (пути к ним)
    image_paths: Optional[List[str]] = None

    # Пользователь (пока просто user_id)
    user_id: Optional[int] = None

class ListingSchema(ListingBase):
    id: int
    image_base64: str | None = None

    class Config:
        orm_mode = True

class ListingRead(ListingBase):
    owner_name: str
    owner_email: str
    owner_phone: str
    image_base64: str | None = None
    liked_user_ids: list[int] = []

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    created_at: datetime
    photo_base64: str | None = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
