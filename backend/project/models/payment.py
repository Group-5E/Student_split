from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, CheckConstraint, Numeric

from .base import db

# --/ !!! >
# --[ This class records direct payments between students to settle debts
# --[ When a payment is made, the relevant ExpenseSplit rows are marked as settled
# --[ payer_id and payee_id cannot be the same (enforced by CheckConstraint) and amount must be positive
# --[ note is optional and can be used to clarify what the payment was for (e.g. 'paid Alice back for groceries')
class Payment(db.Model):
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
# --[ PAYMENT CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ CREATE PAYMENT !!! >
# --[ This function records a payment from one student to another within a household
def create_payment(household_id: int, payer_id: int, payee_id: int,
                   amount: float, note: str = None):
    payment = Payment(
        household_id=household_id,
        payer_id=payer_id,
        payee_id=payee_id,
        amount=amount,
        note=note
    )
    db.session.add(payment)
    db.session.commit()
    db.session.refresh(payment)
    return payment