from sqlalchemy.orm import relationship
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from .base import db

# --/ !!! >
# --[ This class stores student account information
# --[ allow_multiple_households is False by default as most students only belong to one household at a time
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id                          = Column(Integer, primary_key=True)
    username                    = Column(String(50),  unique=True, nullable=False)
    email                       = Column(String(255), unique=True, nullable=False)
    password_hash               = Column(String(255), nullable=False)
    name                        = Column(String(100), nullable=False)
    allow_multiple_households   = Column(Boolean, default=False, nullable=False)
    # is_active                   = Column(Boolean, default=True,  nullable=False)
    created_at                  = Column(DateTime, server_default=func.now())
    last_active_at              = Column(DateTime, onupdate=func.now())

    memberships       = relationship("HouseholdMember", back_populates="user")
    expenses_paid     = relationship("Expense",         back_populates="paid_by")
    splits            = relationship("ExpenseSplit",     back_populates="user")
    payments_sent     = relationship("Payment", foreign_keys="Payment.payer_id", back_populates="payer")
    payments_received = relationship("Payment", foreign_keys="Payment.payee_id", back_populates="payee")

# --/ !!! >
# --[ USER CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ CREATE USER !!! >
# --[ This function creates a new student account
def create_user(username: str, email: str, password_hash: str, name: str):
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        name=name
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user

# --[ GET USER !!! >
# --[ This function fetches a student account by ID and returns None if not found 
def get_user(user_id: int):
    return db.session.get(User, user_id)

# --[ UPDATE USER !!! >
# --[ This function updates a students account details and only updates inputted fields 
def update_user(user_id: int, **kwargs):
    user = db.session.get(User, user_id)
    if not user:
        return None
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.last_active_at = datetime.now()
    db.session.commit()
    db.session.refresh(user)
    return user

# --[ DELETE USER !!! >
# --[ This function deactivates a student account without deleting it
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return None
    user.is_active = False
    db.session.commit()
    return user

    