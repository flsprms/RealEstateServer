from pydantic import BaseModel

class ListingBase(BaseModel):
    title: str
    price: int
    image_path: str | None = None

class Listing(ListingBase):
    id: int

    class Config:
        orm_mode = True
