from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from model.model import Item, Volunteer
from model.database import Session as DBSession

router = APIRouter()


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


@router.get("/volunteers",tags=["volunteers"])
def read_volunteers(db: Session = Depends(get_db)):
    volunteers = db.query(Volunteer).all()
    return volunteers

@router.get("/items", tags=["Items"])
def read_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items

