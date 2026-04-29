# --[ models.py ]~
# --[ This file defines all of the database tables and views for StudentSplit.
# --[ This file uses SQLAlchemy ORM with declarative base.

# --/ !!! >
# --[ Imports
import enum
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime,
    ForeignKey, Enum, Text, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func, text

Base = declarative_base()

# --/ !!! >
# --[ This class stores student account information
# --[ allow_multiple_households is False by default as most students only belong to one household at a time    
class User(Base):
    __tablename__ = "users"

    id                          = Column(Integer, primary_key=True)
    username                    = Column(String(50),  unique=True, nullable=False)
    email                       = Column(String(255), unique=True, nullable=False)
    password_hash               = Column(String(255), nullable=False)
    name                        = Column(String(100), nullable=False)
    allow_multiple_households   = Column(Boolean, default=False, nullable=False)
    is_active                   = Column(Boolean, default=True,  nullable=False)
    created_at                  = Column(DateTime, server_default=func.now())
    last_active_at              = Column(DateTime, onupdate=func.now())

# --/ !!! >
# --[ This class represents a shared student property, like an apartment or dorm room
# --[ A household groups students together for expense tracking
# --[ created_by stores the user who set the household up
class Household(Base):
    __tablename__ = "households"

    id                          = Column(Integer, primary_key=True)
    name                        = Column(String(100), nullable=False)
    address                     = Column(String(255))
    created_by                  = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at                  = Column(DateTime, server_default=func.now())
    is_active                   = Column(Boolean, default=True, nullable=False)

# --/ !!! >
# --[ This class links users to households and tracks their role and membership status
# --[ A user can only appear once per household (enforced by UniqueConstraint on user_id + household_id)
# --[ left_at being NULL means that the user is still active in the household
class HouseholdMember(Base):
    __tablename__ = "household_members"
    __table_args__ = (
        UniqueConstraint("user_id", "household_id", name="uq_user_household"),
    )

    id                          = Column(Integer, primary_key=True)
    user_id                     = Column(Integer, ForeignKey("users.id"),      nullable=False)
    household_id                = Column(Integer, ForeignKey("households.id"), nullable=False)
    role                        = Column(String(10), default="member",         nullable=False)     # admin or member
    joined_at                   = Column(DateTime, server_default=func.now())
    left_at                     = Column(DateTime)                                                 # NULL = still active
    is_active                   = Column(Boolean, default=True, nullable=False)

# --/ !!! >
# --[ This class represents an expense paid by a student on behalf of a household
# --[ split_type determines how the cost is divided between members
# --[ is_deleted deletes record for users but keeps for debt tracking
class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_expense_positive"),
    )

    id                          = Column(Integer, primary_key=True)
    household_id                = Column(Integer, ForeignKey("households.id"), nullable=False)
    paid_by_id                  = Column(Integer, ForeignKey("users.id"),      nullable=False)
    description                 = Column(String(255), nullable=False)
    amount                      = Column(Numeric(10, 2), nullable=False)                            # Numeric (avoids float rounding errors on money)
    split_type                  = Column(String(15), default="equal",     nullable=False)           # [equal, percentage, fixed]
    category                    = Column(String(20), default="other")                               # [rent, utilities, groceries, internet, other]
    notes                       = Column(Text)
    expense_date                = Column(DateTime, nullable=False)
    created_at                  = Column(DateTime, server_default=func.now())
    is_deleted                  = Column(Boolean, default=False, nullable=False)                    # deletes for users but keeps for debt tracking 


# --/ !!! >
# --[ This class represents how an expense is split between household members
# --[ amount_owed is always stored as the resolved £ value regardless of whether the original split was equal, percentage, or fixed
# --[ is_settled is flipped when a payment is recorded
class ExpenseSplit(Base):
    __tablename__ = "expense_splits"
    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", name="uq_split_per_user"),
        CheckConstraint("amount_owed >= 0", name="ck_split_positive"),
    )

    id                          = Column(Integer, primary_key=True)
    expense_id                  = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_id                     = Column(Integer, ForeignKey("users.id"),    nullable=False)
    amount_owed                 = Column(Numeric(10, 2), nullable=False)                            # always the £ amount, never a %
    is_settled                  = Column(Boolean, default=False, nullable=False)
    settled_at                  = Column(DateTime)                                                  # NULL until marked as settled

# --/ !!! >
# --[ This class records direct payments between students to settle debts
# --[ When a payment is made, the relevant ExpenseSplit rows are marked as settled
# --[ payer_id and payee_id cannot be the same (enforced by CheckConstraint) and amount must be positive
# --[ note is optional and can be used to clarify what the payment was for (e.g. 'paid Alice back for groceries')
class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("payer_id != payee_id", name="ck_no_self_payment"),
        CheckConstraint("amount > 0",           name="ck_payment_positive"),
    )

    id           = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey("households.id"), nullable=False)
    payer_id     = Column(Integer, ForeignKey("users.id"),      nullable=False)
    payee_id     = Column(Integer, ForeignKey("users.id"),      nullable=False)
    amount       = Column(Numeric(10, 2), nullable=False)
    note         = Column(String(255))
    created_at   = Column(DateTime, server_default=func.now())    