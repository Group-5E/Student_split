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

# --[ This function fetches a student account by ID and returns None if not found 
def get_user(session: Session, user_id: int):
    return session.get(User, user_id)

# --[ This function updates a students account details and only updates inputted fields 
def update_user(session: Session, user_id: int, **kwargs):
    user = session.get(User, user_id)
    if not user:
        return None
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.last_active_at = datetime.now()
    session.commit()
    session.refresh(user)
    return user