import csv
from sqlalchemy.orm import sessionmaker
from model.model import Item, Category, engine

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
        category_code = row['CODE'][:2]

        # Find the category by code
        category = session.query(Category).filter_by(id=category_code).first()
        if not category:
            # If the category does not exist, create a new one with a default name
            category = Category(id=category_code, name='Default Category Name')
            session.add(category)
            session.commit()  # Commit to get the category ID

        # Find the item by code
        item = session.query(Item).filter_by(code=row['CODE']).first()
        if item:
            # Update existing record
            item.item_name = row['Name']
            item.qty = row['Qty']
            item.unit = row['Unit']
            item.category_id = category.id
        else:
            # Add new record
            new_item = Item(
                code=row['CODE'],
                item_name=row['Name'],
                qty=row['Qty'],
                unit=row['Unit'],
                category_id=category.id
            )
            session.add(new_item)

# Commit the transaction
session.commit()

# Close the session
session.close()