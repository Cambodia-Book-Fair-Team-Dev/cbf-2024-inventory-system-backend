from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database connection setup
DATABASE_URL = "postgresql://cbf:cbf2024@68.183.186.239:5432/cbf2024-inventory"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
