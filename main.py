from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"Welcome to Inventory System CBF 2024 yeeeeeeeeeeeee"}

