from datetime import datetime
from dataclasses import dataclass
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func, UniqueConstraint
from project.models.users import User
from .base import db

# --/ !!! >
# --[ This class represents a shared student property, like an apartment or dorm room
# --[ A household groups students together for expense tracking
# --[ created_by stores the user who set the household up
@dataclass
class Household(db.Model):
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
class HouseholdMember(db.Model):
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

# --[ CREATE HOUSEHOLD !!! >
# --[ This function creates a new household and adds the creator as an admin member
def create_household(name: str, created_by: int, address: str = None):
    household = Household(
        name=name,
        address=address,
        created_by=created_by
    )
    db.session.add(household)
    db.session.flush()                     # gets the household ID *before* committing
    member = HouseholdMember(
        user_id=created_by,
        household_id=household.id,
        role="admin"
    )
    db.session.add(member)
    db.session.commit()
    db.session.refresh(household)
    return household

# --/ !!! >
# --[ HOUSEHOLD CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ GET HOUSEHOLD !!! >
# --[ This function fetches a household by ID and returns None if not found
def get_household(household_id: int):
    return db.session.get(Household, household_id)

# --[ UPDATE HOUSEHOLD !!! >
# --[ This function updates a household's details and only updates inputted fields
# --[ Only admin members can update household details
def add_member(user_id: int, household_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return None
    if not user.allow_multiple_households:
        existing = db.session.query(HouseholdMember).filter_by(user_id=user_id, is_active=True).first()
        if existing:
            raise ValueError("User is already in a household. Enable allow_multiple_households to join another.")
    member = HouseholdMember(
        user_id=user_id,
        household_id=household_id,
        role="member"
    )
    db.session.add(member)
    db.session.commit()
    db.session.refresh(member)
    return member

# --[ REMOVE MEMBER !!! >
# --[ This function removes a member from a household by deactivating their membership
def remove_member(user_id: int, household_id: int):
    member = db.session.query(HouseholdMember).filter_by(
        user_id=user_id,
        household_id=household_id,
        is_active=True
    ).first()
    if not member:
        return None
    member.is_active = False
    member.left_at = datetime.now()
    db.session.commit()
    return member

# --/ !!! >
# --[ EXPENSE SPLIT CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ SETTLE SPLIT !!! >
# --[ This function flags an individual split as settled and records the time
def settle_split(split_id: int):
    from project.models.expenses import ExpenseSplit

    split = db.session.get(ExpenseSplit, split_id)
    if not split:
        return None
    split.is_settled = True
    split.settled_at = datetime.now()
    db.session.commit()
    return split
