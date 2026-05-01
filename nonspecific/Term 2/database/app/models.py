# --[ models.py ] !!! >~
# --[ This file defines all of the database tables and views for StudentSplit
# --[ This file uses SQLAlchemy ORM with declarative base

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

    # --[ Relationships !!! >
    memberships       = relationship("HouseholdMember", back_populates="user")
    expenses_paid     = relationship("Expense",         back_populates="paid_by")
    splits            = relationship("ExpenseSplit",     back_populates="user")
    payments_sent     = relationship("Payment", foreign_keys="Payment.payer_id", back_populates="payer")
    payments_received = relationship("Payment", foreign_keys="Payment.payee_id", back_populates="payee")

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

    # --[ Relationships !!! >
    creator  = relationship("User",            foreign_keys=[created_by])
    members  = relationship("HouseholdMember", back_populates="household")
    expenses = relationship("Expense",         back_populates="household")
    payments = relationship("Payment",         back_populates="household")

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
    
    # --[ Relationships !!! >
    user      = relationship("User",      back_populates="memberships")
    household = relationship("Household", back_populates="members")

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

    # --[ Relationships !!! >
    household = relationship("Household",    back_populates="expenses")
    paid_by   = relationship("User",         back_populates="expenses_paid")
    splits    = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")

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

    # --[ Relationships !!! >
    expense = relationship("Expense", back_populates="splits")
    user    = relationship("User",    back_populates="splits")

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

    id                          = Column(Integer, primary_key=True)
    household_id                = Column(Integer, ForeignKey("households.id"), nullable=False)
    payer_id                    = Column(Integer, ForeignKey("users.id"),      nullable=False)
    payee_id                    = Column(Integer, ForeignKey("users.id"),      nullable=False)
    amount                      = Column(Numeric(10, 2), nullable=False)
    note                        = Column(String(255))
    created_at                  = Column(DateTime, server_default=func.now())    

    # --[ Relationships !!! >
    household = relationship("Household", back_populates="payments")
    payer     = relationship("User", foreign_keys=[payer_id], back_populates="payments_sent")
    payee     = relationship("User", foreign_keys=[payee_id], back_populates="payments_received")

# --/ !!! >
# --[ SQL view definitions, built on top of the core tables
# --[ Call create_views(engine) after Base.metadata.create_all(engine)

# --[ How much each student owes each other within a household
# --[ Excludes the payer's own split row (user_id != paid_by_id)
DEBT_SUMMARY_VIEW = """
CREATE VIEW IF NOT EXISTS v_debt_summary AS
SELECT
    es.user_id AS debtor_id,
    e.paid_by_id AS creditor_id,
    e.household_id,
    SUM(CASE WHEN NOT es.is_settled THEN es.amount_owed ELSE 0 END) AS amount_outstanding,
    SUM(CASE WHEN es.is_settled THEN es.amount_owed ELSE 0 END) AS total_settled,
    SUM(es.amount_owed) AS total_owed
FROM expense_splits es
JOIN expenses e ON e.id = es.expense_id
WHERE e.is_deleted = 0
  AND es.user_id != e.paid_by_id
GROUP BY es.user_id, e.paid_by_id, e.household_id;
"""

# --[ Aggregated expense and balance stats per household
HOUSEHOLD_STATS_VIEW = """
CREATE VIEW IF NOT EXISTS v_household_stats AS
SELECT
    h.id AS household_id,
    h.name AS household_name,
    COUNT(DISTINCT e.id) AS total_expenses,
    COALESCE(SUM(e.amount), 0) AS total_spent,
    COALESCE(SUM(CASE WHEN es.is_settled = 1 THEN es.amount_owed END), 0) AS total_settled,
    COALESCE(SUM(CASE WHEN es.is_settled = 0 THEN es.amount_owed END), 0) AS total_outstanding,
    COUNT(DISTINCT hm.user_id) AS member_count
FROM households h
LEFT JOIN expenses e ON e.household_id = h.id AND e.is_deleted = 0
LEFT JOIN expense_splits es ON es.expense_id = e.id
LEFT JOIN household_members hm ON hm.household_id = h.id AND hm.is_active = 1
GROUP BY h.id, h.name;
"""

# --[ Per user summary of expenses paid, splits involved in, and payments made
USER_ACTIVITY_VIEW = """
CREATE VIEW IF NOT EXISTS v_user_activity AS
SELECT
    u.id AS user_id,
    u.username,
    COUNT(DISTINCT e.id) AS expenses_paid_count,
    COALESCE(SUM(e.amount), 0) AS total_paid_out,
    COUNT(DISTINCT es.id) AS splits_involved_in,
    COALESCE(SUM(es.amount_owed), 0) AS total_owed_across_splits,
    COUNT(DISTINCT p.id) AS payments_made,
    u.last_active_at
FROM users u
LEFT JOIN expenses e ON e.paid_by_id = u.id AND e.is_deleted = 0
LEFT JOIN expense_splits es ON es.user_id = u.id
LEFT JOIN payments p ON p.payer_id = u.id
GROUP BY u.id, u.username, u.last_active_at;
"""

# --[ Net balance per student per household
# --[ Positive = owed money, Negative = owes money
USER_BALANCE_VIEW = """
CREATE VIEW IF NOT EXISTS v_user_balance AS
SELECT
    hm.user_id,
    hm.household_id,
    COALESCE(paid.total_paid, 0) AS total_paid,
    COALESCE(owed.total_owed, 0) AS total_owed,
    COALESCE(paid.total_paid, 0) - COALESCE(owed.total_owed, 0) AS net_balance
FROM household_members hm
LEFT JOIN (
    SELECT paid_by_id AS user_id, household_id, SUM(amount) AS total_paid
    FROM expenses WHERE is_deleted = 0
    GROUP BY paid_by_id, household_id
) paid ON paid.user_id = hm.user_id AND paid.household_id = hm.household_id
LEFT JOIN (
    SELECT es.user_id, e.household_id, SUM(es.amount_owed) AS total_owed
    FROM expense_splits es
    JOIN expenses e ON e.id = es.expense_id AND e.is_deleted = 0
    WHERE es.user_id != e.paid_by_id
    GROUP BY es.user_id, e.household_id
) owed ON owed.user_id = hm.user_id AND owed.household_id = hm.household_id
WHERE hm.is_active = 1;
"""


# --[ Executes all view DDL against the database
# --[ Must be called after Base.metadata.create_all(engine)
# --[ Safe to re-run as all views use CREATE VIEW IF NOT EXISTS
def create_views(engine):
    with engine.connect() as conn:
        for view_sql in [DEBT_SUMMARY_VIEW, HOUSEHOLD_STATS_VIEW, USER_ACTIVITY_VIEW, USER_BALANCE_VIEW]:
            conn.execute(text(view_sql))
        conn.commit()