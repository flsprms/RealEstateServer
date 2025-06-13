from datetime import datetime, UTC
from sqlalchemy.orm import Session

from models import Listing, ListingPhoto
from schemas import ListingBase


def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Listing).all()

def create_listing(db: Session, listing_data: ListingBase):
    # logging.info("Начало создания нового объявления")

    title = (f"{listing_data.rooms}-к. квартира, "
             f"{listing_data.total_area} м², "
             f"{listing_data.floor}/{listing_data.total_floors} эт.")

    db_listing = Listing(
        title=title,
        price=listing_data.price,
        rooms=listing_data.rooms,
        total_area=listing_data.total_area,
        kitchen_area=listing_data.kitchen_area,
        floor=listing_data.floor,
        total_floors=listing_data.total_floors,
        deposit=listing_data.deposit,
        commission_percent=listing_data.commission_percent,
        utilities_separate=listing_data.utilities_separate,
        allowed_children=listing_data.allowed_children,
        allowed_pets=listing_data.allowed_pets,
        allowed_smoking=listing_data.allowed_smoking,
        description=listing_data.description,
        address_city=listing_data.address_city,
        address_street=listing_data.address_street,
        address_house=listing_data.address_house,
        type=listing_data.type,
        user_id=listing_data.user_id,
        created_at=datetime.now(UTC)
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)

    if listing_data.image_paths:
        for path in listing_data.image_paths:
            db_photo = ListingPhoto(listing_id=db_listing.id, image_path=path)
            db.add(db_photo)
        db.commit()

    # logging.info(f"Создано объявление id={db_listing.id} "
    #              f"name={db_listing.title} "
    #              f"от пользователя id={db_listing.user_id}")

    return db_listing
