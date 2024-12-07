import csv
from sqlalchemy.orm import sessionmaker
from model.model import Volunteer, engine  # Import the engine instance

# Create a session factory bound to the engine
Session = sessionmaker(bind=engine)

# Create a new session from the session factory
session = Session()

# Path to your CSV file
csv_file_path = 'import_file/CBF_11th_Data.csv'

# Read the CSV file and add/update records
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Find the volunteer by id
        volunteer = session.query(Volunteer).filter_by(id=row['id']).first()
        if volunteer:
            # Update existing record
            volunteer.name = row['name']
            volunteer.kh_name = row['kh_name']
            volunteer.team = row['team']
            volunteer.kh_team = row['kh_team']
        else:
            # Add new record
            new_volunteer = Volunteer(
                id=row['id'],
                name=row['name'],
                kh_name=row['kh_name'],
                team=row['team'],
                kh_team=row['kh_team']
            )
            session.add(new_volunteer)

# Commit the transaction
session.commit()

# Close the session
session.close()
