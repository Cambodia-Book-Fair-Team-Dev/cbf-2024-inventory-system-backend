from barcode import Code128
from barcode.writer import ImageWriter
from sqlalchemy.exc import NoResultFound
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Transaction
from sqlalchemy.orm import Session
from model.model import Item, Volunteer, Transaction
from model.database import Session as DBSession
import uuid
import pytz

router = APIRouter()


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


def get_cambodia_time():
    cambodia_timezone = pytz.timezone('Asia/Phnom_Penh')
    return datetime.now(cambodia_timezone)

# Request Models


class BorrowRequest(BaseModel):
    item_code: str
    qty: int = Field(..., gt=0, description="Quantity must be greater than 0")


class BorrowedItemResponse(BaseModel):
    transaction_id: str
    item_code: str
    volunteer_name: str
    team: str
    item_name: str
    qty_borrowed: int
    borrow_time: datetime
    return_time: Optional[datetime] = None
    status: str


class ReturnItem(BaseModel):
    transaction_id: str
    qty_returned: int
    status: str


class ReturnRequest(BaseModel):
    items: List[ReturnItem]


@router.get("/items", tags=["Items"])
def read_items(db: Session = Depends(get_db)):
    items = db.query(Item).order_by(Item.code).all()
    return items


@router.get("/borrowed-items", response_model=List[BorrowedItemResponse], tags=["Items"])
def get_borrowed_items(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    borrowed_items = []

    for transaction in transactions:
        volunteer = db.query(Volunteer).filter(
            Volunteer.id == transaction.volunteer_id).first()
        item = db.query(Item).filter(
            Item.code == transaction.item_code).first()

        borrowed_items.append(BorrowedItemResponse(
            transaction_id=transaction.transaction_id,
            item_code=transaction.item_code,
            volunteer_name=volunteer.name,
            team=volunteer.team,
            item_name=item.item_name,
            qty_borrowed=transaction.qty_borrowed,
            borrow_time=transaction.borrow_time.astimezone(
                pytz.timezone('Asia/Phnom_Penh')),
            return_time=transaction.return_time.astimezone(pytz.timezone(
                'Asia/Phnom_Penh')) if transaction.return_time else None,
            status=transaction.status
        ))

    return borrowed_items


@router.get("/scan/item/{item_code}", tags=["Items"])
def scan_items(item_code: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.code == item_code).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Borrow Endpoint


@router.post("/volunteer/{volunteer_id}/borrow", tags=["Scan"])
def borrow_item(volunteer_id: str, request: BorrowRequest, db: Session = Depends(get_db)):
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    item = db.query(Item).filter(Item.code == request.item_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.qty < request.qty:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    transaction = Transaction(
        transaction_id=str(uuid.uuid4()),
        volunteer_id=volunteer_id,
        item_code=request.item_code,
        qty_borrowed=request.qty,
        borrow_time=get_cambodia_time(),
        status="borrowed"
    )
    item.qty -= request.qty
    db.add(transaction)
    db.add(item)
    db.commit()
    db.refresh(transaction)
    return {"message": "Item borrowed successfully", "transaction": transaction}


@router.post("/volunteer/{volunteer_id}/return", tags=["Scan"])
def return_items(volunteer_id: str, request: ReturnRequest, db: Session = Depends(get_db)):
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    for item in request.items:
        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == item.transaction_id,
            Transaction.status == "borrowed"
        ).first()
        if not transaction:
            raise HTTPException(
                status_code=404, detail=f"Transaction {item.transaction_id} not found")

        if item.status not in ["returned", "lost", "used up"]:
            raise HTTPException(
                status_code=400, detail="Invalid status")

        if item.qty_returned > transaction.qty_borrowed:
            raise HTTPException(
                status_code=400, detail="Returned quantity exceeds borrowed quantity")

        # If the returned quantity is equal to the borrowed quantity, do not update
        if item.qty_returned == transaction.qty_borrowed:
            transaction.status = item.status
            transaction.return_time = get_cambodia_time()
        else:
            # Update the original transaction to reflect the returned/lost/used-up items
            transaction.qty_borrowed -= item.qty_returned

            # Create a new transaction for the kept items
            kept_qty = transaction.qty_borrowed
            new_transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                volunteer_id=volunteer_id,
                item_code=transaction.item_code,
                qty_borrowed=kept_qty,
                borrow_time=transaction.borrow_time,
                status="borrowed"
            )
            db.add(new_transaction)

            # Update the original transaction to reflect the returned/lost/used-up items
            transaction.qty_borrowed = item.qty_returned
            transaction.status = item.status
            transaction.return_time = get_cambodia_time() if item.status == "returned" else None

        # Update stock if the status is "returned"
        if item.status == "returned":
            item_record = db.query(Item).filter(
                Item.code == transaction.item_code).first()
            if item_record:
                item_record.qty += item.qty_returned
                db.add(item_record)

        db.add(transaction)

    db.commit()
    return {"message": "Items processed successfully"}


@router.post("/scan/transaction", tags=["Scan"])
def create_transaction(volunteer_id: str, item_code: str, qty_borrowed: int, db: Session = Depends(get_db)):
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    item = db.query(Item).filter(Item.code == item_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.qty < qty_borrowed:
        raise HTTPException(
            status_code=400, detail="Not enough stock available")

    # Decrement the stock quantity
    item.qty -= qty_borrowed
    db.add(item)

    # Create the transaction
    transaction = Transaction(
        transaction_id=str(uuid.uuid4()),
        volunteer_id=volunteer_id,
        item_code=item_code,
        qty_borrowed=qty_borrowed,
        borrow_time=get_cambodia_time(),
        status="borrowed"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return {"message": "Transaction created successfully", "transaction": transaction}


@router.post("/item/return/transaction", tags=["Scan"])
def return_transaction(transaction_id: str, qty_returned: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    item = db.query(Item).filter(Item.code == transaction.item_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if transaction.status != "borrowed":
        raise HTTPException(
            status_code=400, detail="Item has already been returned or is not borrowed")

    # Increment the stock quantity
    item.qty += qty_returned
    db.add(item)

    # Update the transaction
    transaction.return_time = get_cambodia_time()
    transaction.status = "returned"
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return {"message": "Item returned successfully", "transaction": transaction}


@router.get("/volunteer/{volunteer_id}/borrowed-items", tags=["Volunteers"])
def get_borrowed_items(volunteer_id: str, db: Session = Depends(get_db)):
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    transactions = db.query(Transaction).filter(
        Transaction.volunteer_id == volunteer_id, Transaction.status == "borrowed").all()
    if not transactions:
        raise HTTPException(
            status_code=404, detail="No borrowed items found for this volunteer")

    borrowed_items = []
    for transaction in transactions:
        item = db.query(Item).filter(
            Item.code == transaction.item_code).first()
        borrowed_items.append({
            "transaction_id": transaction.transaction_id,
            "item_code": item.code,
            "item_name": item.item_name,
            "qty_borrowed": transaction.qty_borrowed,
            "borrow_time": transaction.borrow_time.astimezone(pytz.timezone('Asia/Phnom_Penh'))
        })

    return {"volunteer_id": volunteer_id, "borrowed_items": borrowed_items}

# Add QTY for each Product


class UpdateQtyRequest(BaseModel):
    qty: int


@router.put("/items/{item_code}/update-qty", tags=["Items"])
def update_item_qty(item_code: str, request: UpdateQtyRequest, db: Session = Depends(get_db)):
    try:
        item = db.query(Item).filter(Item.code == item_code).one()
        item.qty += request.qty
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"message": "Item quantity updated successfully", "item": item}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Item not found")


class NewItemRequest(BaseModel):
    category_id: str
    item_name: str
    qty: int
    unit: str


@router.post("/items", tags=["Items"])
def add_new_item(request: NewItemRequest, db: Session = Depends(get_db)):
    # Get the highest item code in the specified category
    highest_item_code = db.query(Item).filter(
        Item.category_id == request.category_id).order_by(Item.code.desc()).first()

    if highest_item_code:
        # Extract the numeric part of the item code and increment it
        last_number = int(highest_item_code.code.split('-')[1])
        new_number = last_number + 1
    else:
        # If no items exist in the category, start with 1
        new_number = 1

    # Generate the new item code with four digits
    item_code = f"{request.category_id}-{new_number:02d}-0001"

    # Create the new item
    new_item = Item(
        category_id=request.category_id,
        code=item_code,
        item_name=request.item_name,
        qty=request.qty,
        unit=request.unit
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"message": "New item added successfully", "item": new_item}
