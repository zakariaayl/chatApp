from connect_db import get_connection
from models import db, User, Message, Friendship

def create_tables():
    engine = get_connection()
    db.metadata.create_all(engine)
    print("Database tables created successfully!")

# Call the function to create the tables
create_tables()