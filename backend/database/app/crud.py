# --[ crud.py ] !!! >~
# --[ This file contains all CRUD functions for the StudentSplit database
# --[ All functions take a SQLAlchemy session as their first argument
# --[ ------------------------------------ >

# --/ !!! >
# --[ Imports 
from app.models import User, Household, HouseholdMember, Expense, ExpenseSplit, Payment
from sqlalchemy.orm import Session
from datetime import datetime

# --/ !!! >
# --[ USER CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ CREATE USER !!! >
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

# --[ GET USER !!! >
# --[ This function fetches a student account by ID and returns None if not found 
def get_user(session: Session, user_id: int):
    return session.get(User, user_id)

# --[ UPDATE USER !!! >
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

# --[ DELETE USER !!! >
# --[ This function deactivates a student account without deleting it
def delete_user(session: Session, user_id: int):
    user = session.get(User, user_id)
    if not user:
        return None
    user.is_active = False
    session.commit()
    return user

# --/ !!! >
# --[ HOUSEHOLD CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ CREATE HOUSEHOLD !!! >
# --[ This function creates a new household and adds the creator as an admin member
def create_household(session: Session, name: str, created_by: int, address: str = None):
    household = Household(
        name=name,
        address=address,
        created_by=created_by
    )
    session.add(household)
    session.flush()                     # gets the household ID *before* committing
    member = HouseholdMember(
        user_id=created_by,
        household_id=household.id,
        role="admin"
    )
    session.add(member)
    session.commit()
    session.refresh(household)
    return household

# --[ GET HOUSEHOLD !!! >
# --[ This function fetches a household by ID and returns None if not found
def get_household(session: Session, household_id: int):
    return session.get(Household, household_id)

# --[ UPDATE HOUSEHOLD !!! >
# --[ This function updates a household's details and only updates inputted fields
# --[ Only admin members can update household details
def add_member(session: Session, user_id: int, household_id: int):
    user = session.get(User, user_id)
    if not user:
        return None
    if not user.allow_multiple_households:
        existing = session.query(HouseholdMember).filter_by(user_id=user_id, is_active=True).first()
        if existing:
            raise ValueError("User is already in a household. Enable allow_multiple_households to join another.")
    member = HouseholdMember(
        user_id=user_id,
        household_id=household_id,
        role="member"
    )
    session.add(member)
    session.commit()
    session.refresh(member)
    return member

# --[ REMOVE MEMBER !!! >
# --[ This function removes a member from a household by deactivating their membership
def remove_member(session: Session, user_id: int, household_id: int):
    member = session.query(HouseholdMember).filter_by(
        user_id=user_id,
        household_id=household_id,
        is_active=True
    ).first()
    if not member:
        return None
    member.is_active = False
    member.left_at = datetime.now()
    session.commit()
    return member

# --/ !!! >
# --[ EXPENSE CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ CREATE EXPENSE !!! >
# --[ This function creates an expense 
# --[ Automatically generates equal splits for all active household members
def create_expense(session: Session, household_id: int, paid_by_id: int, description: str,
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
    session.add(expense)
    session.flush()  # get expense ID before committing

    # --[ Generates equal splits for all active members:
    members = session.query(HouseholdMember).filter_by(
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
        session.add(split)

    session.commit()
    session.refresh(expense)
    return expense

# --[ GET EXPENSES !!! >
# --[ This function fetches all expenses for a household except "deleted" expenses
def get_expenses(session: Session, household_id: int):
    return session.query(Expense).filter_by(
        household_id=household_id,
        is_deleted=False
    ).all()

# --[ DELETE EXPENSE !!! >
# --[ This function soft deletes an expense but preserves the record for data purposes
def delete_expense(session: Session, expense_id: int):
    expense = session.get(Expense, expense_id)
    if not expense:
        return None
    expense.is_deleted = True
    session.commit()
    return expense

# --/ !!! >
# --[ EXPENSE SPLIT CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ SETTLE SPLIT !!! >
# --[ This function flags an individual split as settled and records the time
def settle_split(session: Session, split_id: int):
    split = session.get(ExpenseSplit, split_id)
    if not split:
        return None
    split.is_settled = True
    split.settled_at = datetime.now()
    session.commit()
    return split

# --/ !!! >
# --[ PAYMENT CRUD FUNCTIONS
# --[ ------------------------------------ >

# --[ CREATE PAYMENT !!! >
# --[ This function records a payment from one student to another within a household
def create_payment(session: Session, household_id: int, payer_id: int, payee_id: int,
                   amount: float, note: str = None):
    payment = Payment(
        household_id=household_id,
        payer_id=payer_id,
        payee_id=payee_id,
        amount=amount,
        note=note
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment