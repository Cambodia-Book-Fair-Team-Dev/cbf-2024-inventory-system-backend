import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Transaction
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


@router.get("/volunteers",tags=["Volunteers"])
def read_volunteers(db: Session = Depends(get_db)):
    volunteers = db.query(Volunteer).all()
    return volunteers


@router.get("/scan/volunteer/{volunteer_id}", tags=["Volunteers"])
def scan_volunteers(volunteer_id: str, db: Session = Depends(get_db)):
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer
