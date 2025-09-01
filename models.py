from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(String)
    balance = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    transactions = relationship("Transactions", back_populates="user")
    recipients = relationship("Users", secondary="transactions", back_populates="senders")
    senders = relationship("Users", secondary="transactions", back_populates="recipients")

    

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

    user = relationship("User", back_populates="transactions")
    reference_transaction = relationship("Transactions", remote_side=[id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    