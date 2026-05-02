# --[ main.py ]~
# --[ This file is the entry point for StudentSplit
# --[ This creates the database and all tables on startup

from sqlalchemy import create_engine
from app.models import Base, create_views

# --[ SQLite used for local development, will be swapped for PostgreSQL in production
engine = create_engine("sqlite:///studentsplit.db", echo=True)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    create_views(engine)
    print("Database and tables created successfully.")