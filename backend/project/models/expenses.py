from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func, UniqueConstraint, CheckConstraint, Numeric, Text

from .base import db

# --/ !!! >
# --[ This class represents an expense paid by a student on behalf of a household
# --[ split_type determines how the cost is divided between members
# --[ is_deleted deletes record for users but keeps for debt tracking
class Expense(db.Model):
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

    # --[ Relationships !!! >
    household = relationship("Household",    back_populates="expenses")
    paid_by   = relationship("User",         back_populates="expenses_paid")
    splits    = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")

# --/ !!! >
# --[ This class represents how an expense is split between household members
# --[ amount_owed is always stored as the resolved £ value regardless of whether the original split was equal, percentage, or fixed
# --[ is_settled is flipped when a payment is recorded
class ExpenseSplit(db.Model):
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

    # --[ Relationships !!! >
    expense = relationship("Expense", back_populates="splits")
    user    = relationship("User",    back_populates="splits")
