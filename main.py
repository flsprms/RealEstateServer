import base64
import os
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import bcrypt

from db import SessionLocal, engine, Base
from models import User, Listing, ListingPhoto, Like
from schemas import UserCreate, UserOut, ListingBase, ListingSchema, UserLogin, UserLoginResponse, ListingPreview, \
    ListingRead
from crud import get_listings, create_listing

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Зависимость - сессия базы
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ListingPhotoBase64(BaseModel):
    base64_data: str  # строка base64 (без data:image/jpeg;base64, если что — обрежем)
    extension: str = ".jpg"  # или ".png" и т.п.

@app.get("/listings/", response_model=list[ListingPreview])
def read_listings(skip: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    listings = get_listings(db, skip=skip, limit=limit)
    result = []

    for listing in listings:
        image_data = None
        if listing.photos:
            first_photo = listing.photos[0]
            if first_photo.image_path and os.path.isfile(first_photo.image_path):
                with open(first_photo.image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode("utf-8")
        db_user = db.query(User).filter(User.id == listing.user_id).first()
        liked_ids = [user.id for user in listing.liked_by_users]
        result.append(ListingPreview(
            id=listing.id,
            title=listing.title,
            price=listing.price,
            owner_name=db_user.name if db_user else "",
            image_base64=image_data,
            liked_by_users=liked_ids,
        ))

    return result

@app.get("/my-listings/", response_model=list[ListingPreview])
def read_my_listings(user_id: int, skip: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    listings = get_listings(db, skip=skip, limit=limit)
    result = []

    for listing in listings:
        if listing.user_id == user_id:
            image_data = None
            if listing.photos:
                first_photo = listing.photos[0]
                if first_photo.image_path and os.path.isfile(first_photo.image_path):
                    with open(first_photo.image_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode("utf-8")
            db_user = db.query(User).filter(User.id == listing.user_id).first()
            liked_ids = [user.id for user in listing.liked_by_users]
            result.append(ListingPreview(
                id=listing.id,
                title=listing.title,
                price=listing.price,
                owner_name=db_user.name,
                image_base64=image_data,
                liked_by_users=liked_ids,
            ))

    return result

@app.get("/liked-listings/", response_model=list[ListingPreview])
def read_liked_listings(user_id: int, skip: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    listings = get_listings(db, skip=skip, limit=limit)
    result = []

    current_user = db.query(User).filter(User.id == user_id).first()

    for listing in listings:
        if current_user in listing.liked_by_users:
            image_data = None
            if listing.photos:
                first_photo = listing.photos[0]
                if first_photo.image_path and os.path.isfile(first_photo.image_path):
                    with open(first_photo.image_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode("utf-8")
            db_user = db.query(User).filter(User.id == listing.user_id).first()
            liked_ids = [user.id for user in listing.liked_by_users]
            result.append(ListingPreview(
                id=listing.id,
                title=listing.title,
                price=listing.price,
                owner_name=db_user.name,
                image_base64=image_data,
                liked_by_users=liked_ids,
            ))

    return result

@app.get("/filtered-listings/", response_model=list[ListingPreview])
def read_filtered_listings(query: str, value: str, db: Session = Depends(get_db)):
    result = []
    listings = []
    if query == "city":
        listings = db.query(Listing).filter(Listing.address_city.ilike(f"%{value}%")).all()
    elif query == "user":
        listings = (
            db.query(Listing)
            .join(User, Listing.user_id == User.id)
            .filter(User.name.ilike(f"%{value}%"))
            .all()
        )
    elif query == "price":
        listings = db.query(Listing).filter(Listing.price <= int(value)).all()

    for listing in listings:
        image_data = None
        if listing.photos:
            first_photo = listing.photos[0]
            if first_photo.image_path and os.path.isfile(first_photo.image_path):
                with open(first_photo.image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode("utf-8")
        db_user = db.query(User).filter(User.id == listing.user_id).first()
        liked_ids = [user.id for user in listing.liked_by_users]
        result.append(ListingPreview(
            id=listing.id,
            title=listing.title,
            price=listing.price,
            owner_name=db_user.name,
            image_base64=image_data,
            liked_by_users=liked_ids,
        ))

    return result

@app.post("/listings/", response_model=ListingSchema)
def create_listing_endpoint(listing: ListingBase, db: Session = Depends(get_db)):
    return create_listing(db, listing)

@app.get("/listing/{listing_id}", response_model=ListingRead)
def read_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=400, detail="Listing not found")
    listing.owner_name = listing.user.name
    listing.owner_email = listing.user.email
    listing.owner_phone = listing.user.phone
    image_data = None
    if listing.photos:
        first_photo = listing.photos[0]
        if first_photo.image_path and os.path.isfile(first_photo.image_path):
            with open(first_photo.image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
    listing.image_base64 = image_data
    listing.liked_user_ids = [user.id for user in listing.liked_by_users]
    return listing

@app.delete("/listing/{listing_id}", status_code=status.HTTP_200_OK)
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=400, detail="Listing not found")
    db.delete(listing)
    db.commit()
    return {"message": "Объявление удалено!!"}

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        hashed_password=bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=UserLoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.checkpw(user.password.encode(), db_user.hashed_password.encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    photo_base64 = None
    if db_user.image_path and os.path.isfile(db_user.image_path):
        with open(db_user.image_path, "rb") as image_file:
            photo_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    return UserLoginResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        phone=db_user.phone,
        created_at=db_user.created_at,
        photo_base64=photo_base64
    )

@app.get("/user-photo/{user_id}")
def get_user_photo(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.image_path:
        raise HTTPException(status_code=404, detail="User or photo not found")

    image_path = user.image_path
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    with open(user.image_path, "rb") as image_file:
        photo_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    return {"image_base64": photo_base64}

@app.post("/user-photo/{user_id}")
def upload_user_photo(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Создаём путь к файлу
    filename = f"static/users/user_{user_id}{os.path.splitext(file.filename)[1]}"
    with open(filename, "wb") as image_file:
        image_file.write(file.file.read())

    # Обновляем путь в БД
    user.image_path = filename
    db.commit()

    return {"message": "Photo uploaded successfully", "image_path": filename}

@app.get("/listing-photo/{listing_id}")
def get_listing_photo(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing or not listing.image_path:
        raise HTTPException(status_code=404, detail="listing or photo not found")

    image_path = listing.image_path

    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(image_path, media_type="image/png")


@app.post("/listing-photo/{listing_id}")
def upload_listing_photo(listing_id: int, photo_data: ListingPhotoBase64, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Создаём путь к файлу
    if "," in photo_data.base64_data:
        _, base64_str = photo_data.base64_data.split(",", 1)
    else:
        base64_str = photo_data.base64_data

    try:
        image_bytes = base64.b64decode(base64_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 string")
    filename = f"static/listings/listing_{listing_id}_{uuid4().hex}{photo_data.extension}"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "wb") as image_file:
        image_file.write(image_bytes)

    new_photo = ListingPhoto(
        listing_id=listing_id,
        image_path=filename,
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)

    return {"message": "Photo uploaded successfully", "id": new_photo.id}

@app.post("/listing-like", status_code=status.HTTP_200_OK)
def like_listing(listing_id: int, user_id: int, db: Session = Depends(get_db), ):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    like = db.query(Like).filter((Like.user_id == user_id) & (Like.listing_id == listing_id)).first()

    if not like:
        like = Like(listing_id=listing_id, user_id=user_id)

        db.add(like)
        db.commit()
        db.refresh(like)
        return {"message": "Лайк добавлен"}

    else:
        return {"message": "Лайк уже был добавлен!"}

@app.delete("/listing-unlike", status_code=status.HTTP_200_OK)
def unlike_listing(listing_id: int, user_id: int, db: Session = Depends(get_db), ):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    like = db.query(Like).filter((Like.user_id == user_id) & (Like.listing_id == listing_id)).first()

    if like:
        db.delete(like)
        db.commit()
        return {"message": "Лайк был удален!"}

    else:
        return {"message": "Лайк не существует!"}