import csv
from sqlalchemy.orm import sessionmaker
# Import the engine instance and Item model
from model.model import Item, engine

# Create a session factory bound to the engine
Session = sessionmaker(bind=engine)

# Create a new session from the session factory
session = Session()

# Path to your CSV file
csv_file_path = 'import_file/item/catagory_01_filtered.csv'

# Read the CSV file and add/update records
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Extract category from the code
        # Assuming the first two characters represent the category
        category = row['CODE'][:2]

        # Find the item by code
        item = session.query(Item).filter_by(code=row['CODE']).first()
        if item:
            # Update existing record
            item.item_name = row['Name']
            item.qty = row['Qty']
            item.unit = row['Unit']
            item.category = category
        else:
            # Add new record
            new_item = Item(
                code=row['CODE'],
                item_name=row['Name'],
                qty=row['Qty'],
                unit=row['Unit'],
                category=category
            )
            session.add(new_item)

# Commit the transaction
session.commit()

# Close the session
session.close()
