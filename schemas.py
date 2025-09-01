from pydantic import BaseModel
from datetime import datetime

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    password: str
    phone_number: str
    balance: int
    created_at: datetime
    updated_at: datetime

class TransactionSchema(BaseModel):
    id: int
    user_id: int
    transaction_type: str
    amount: int
    description: str
    reference_transaction_id: int
    recipient_id: int
    created_at: datetime
    updated_at: datetime


    class Config:
        orm_mode = True 
        arbitrary_types_allowed = True
