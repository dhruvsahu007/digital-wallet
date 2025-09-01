from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(Integer)
    balance = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type = Column(String)
    amount = Column(Integer)
    description = Column(String)
    reference_transaction_id = Column(Integer, ForeignKey("transactions.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


