from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from model.database import Base, engine


class Volunteer(Base):
    __tablename__ = 'volunteer'
    id = Column(String(100), primary_key=True)
    kh_name = Column(String(500))
    kh_team = Column(String(200))
    team = Column(String(100))
    name = Column(String(100))

class Category(Base):
    __tablename__ = 'category'
    id = Column(String(10), primary_key=True)
    name = Column(String(100))

class Item(Base):
    __tablename__ = 'item'
    code = Column(String(100), primary_key=True)
    item_name = Column(String(200))
    qty = Column(Integer)
    unit = Column(String(50))
    category_id = Column(String(10), ForeignKey('category.id'))


class Transaction(Base):
    __tablename__ = 'transaction'
    transaction_id = Column(String(100), primary_key=True)
    volunteer_id = Column(String(100), ForeignKey('volunteer.id'))
    item_code = Column(String(100), ForeignKey('item.code'))
    borrow_time = Column(DateTime)
    return_time = Column(DateTime)
    qty_borrowed = Column(Integer)
    status = Column(String(50))
    is_reusable = Column(Boolean, default=False)


def create_tables():
    Base.metadata.create_all(engine)
