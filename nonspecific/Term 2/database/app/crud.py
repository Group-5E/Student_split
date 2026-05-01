# --[ crud.py ] !!! >~
# --[ This file contains all CRUD functions for the StudentSplit database
# --[ All functions take a SQLAlchemy session as their first argument

# --/ !!! >
# --[ Imports
from app.models import User, Household, HouseholdMember, Expense, ExpenseSplit, Payment
from sqlalchemy.orm import Session
from datetime import datetime

# --/ !!! >
# --[ User CRUD functions

# --[ This function creates a new student account
def create_user(session: Session, username: str, email: str, password_hash: str, name: str):
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        name=name
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

