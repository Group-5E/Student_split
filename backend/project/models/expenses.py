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

# --/ !!! >
# --[ EXPENSE CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ CREATE EXPENSE !!! >
# --[ This function creates an expense 
# --[ Automatically generates equal splits for all active household members
def create_expense(household_id: int, paid_by_id: int, description: str,
                   amount: float, expense_date: datetime, category: str = "other",
                   split_type: str = "equal", notes: str = None):
    expense = Expense(
        household_id=household_id,
        paid_by_id=paid_by_id,
        description=description,
        amount=amount,
        expense_date=expense_date,
        category=category,
        split_type=split_type,
        notes=notes
    )
    db.session.add(expense)
    db.session.flush()  # get expense ID before committing

    # --[ Generates equal splits for all active members:
    members = db.session.query(HouseholdMember).filter_by(
        household_id=household_id,
        is_active=True
    ).all()
    split_amount = round(amount / len(members), 2)
    for member in members:
        split = ExpenseSplit(
            expense_id=expense.id,
            user_id=member.user_id,
            amount_owed=split_amount
        )
        db.session.add(split)

    db.session.commit()
    db.session.refresh(expense)
    return expense

# --[ GET EXPENSES !!! >
# --[ This function fetches all expenses for a household except "deleted" expenses
def get_expenses(household_id: int):
    return db.session.query(Expense).filter_by(
        household_id=household_id,
        is_deleted=False
    ).all()

# --[ DELETE EXPENSE !!! >
# --[ This function soft deletes an expense but preserves the record for data purposes
def delete_expense(expense_id: int):
    expense = db.session.get(Expense, expense_id)
    if not expense:
        return None
    expense.is_deleted = True
    db.session.commit()
    return expense