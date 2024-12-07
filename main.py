from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from model.model import Volunteer, Item, Transaction, create_tables
from model.database import Session as DBSession
from routes.route import router as volunteer_router
app = FastAPI()


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/")
def read_root():
    return {"Welcome to Inventory System CBF 2024 yeeeeeeeeeeeee"}


app.include_router(volunteer_router)
# app.include_router(item_router)
# app.include_router(transaction_router)
