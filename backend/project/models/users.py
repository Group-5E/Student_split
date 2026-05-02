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
