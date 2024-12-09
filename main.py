from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from model.model import Volunteer, Item, Transaction, create_tables
from model.database import Session as DBSession
from routes.volunteer import router as volunteer_router
from routes.items import router as item_router

app = FastAPI()

# Define the origins that should be allowed to make requests to your API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(item_router)
# app.include_router(transaction_router)
