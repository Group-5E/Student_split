from dataclasses import dataclass
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func, UniqueConstraint

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
