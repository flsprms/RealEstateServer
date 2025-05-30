from sqlalchemy.orm import Session
from models import Listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Listing).offset(skip).limit(limit).all()

def create_listing(db: Session, title: str, price: int, image_path: str = None):
    db_listing = Listing(title=title, price=price, image_path=image_path)
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing
