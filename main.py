from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal, engine, Base
import crud, models, schemas

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Зависимость - сессия базы
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/listings/", response_model=list[schemas.Listing])
def read_listings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    listings = crud.get_listings(db, skip=skip, limit=limit)
    return listings

@app.post("/listings/", response_model=schemas.Listing)
def create_listing(listing: schemas.ListingBase, db: Session = Depends(get_db)):
    return crud.create_listing(db, title=listing.title, price=listing.price, image_path=listing.image_path)
