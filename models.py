from sqlalchemy import Column, Integer, String
from db import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Integer)
    image_path = Column(String, nullable=True)
