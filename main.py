from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from model.model import Volunteer, Item, Transaction, create_tables
from model.database import Session as DBSession

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
