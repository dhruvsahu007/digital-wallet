#match with models.py

from pydantic import BaseModel
from datetime import datetime

class UserSchema(BaseModel):
    id: int
    email: str
    password: str
    phone_number: int
    balance: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class TransactionSchema(BaseModel):
    user_id: int
    transaction_type: str
    amount: float
    description: str
    reference_transaction_id: int = None
    recipient_user_id: int = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class TransactionResponseSchema(BaseModel):
    id: int
    user_id: int
    transaction_type: str
    amount: float
    description: str
    reference_transaction_id: int = None
    recipient_user_id: int = None
    created_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class TransferSchema(BaseModel):
    sender_user_id: int
    recipient_user_id: int
    amount: int
    description: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        

