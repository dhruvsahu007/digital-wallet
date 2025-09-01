from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy import Transaction
from sqlalchemy.orm import Session
from database import engine, get_db
from models import User
from schemas import UserSchema
from database import Base
from schemas import TransactionSchema
from schemas import TransferSchema


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/users/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/wallet/{user_id}/balance")
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.id,
        "balance": user.balance,
        "last_updated": user.updated_at
    }


@app.post("/wallet/{user_id}/add-money")
def add_money_to_wallet(user_id: int, transaction: TransactionSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.balance += transaction.amount
    db.commit()
    db.refresh(user)
    return {
        "transaction_id": 123,
        "user_id": user.id,
        "amount": transaction.amount,
        "new_balance": user.balance,
        "transaction_type": "CREDIT"
    }

@app.post("/wallet/{user_id}/withdraw")
def withdraw_money_from_wallet(user_id: int, transaction: TransactionSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    user.balance -= transaction.amount
    db.commit()
    db.refresh(user)
    return {
        "transaction_id": 124,
        "user_id": user.id,
        "amount": transaction.amount,
        "new_balance": user.balance,
        "transaction_type": "DEBIT"
    }


@app.get("/transactions/{user_id}?page=1&limit=10")
def get_transaction_history(user_id: int, db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).offset((page - 1) * limit).limit(limit).all()
    total = db.query(Transaction).filter(Transaction.user_id == user_id).count()
    return {
        "transactions": transactions,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/transactions/detail/{transaction_id}")
def get_transaction_detail(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.post("/transactions")
def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction



@app.post("/transfer")
def create_transfer(transfer: TransferSchema, db: Session = Depends(get_db)):
    sender = db.query(User).filter(User.id == transfer.sender_user_id).first()
    recipient = db.query(User).filter(User.id == transfer.recipient_user_id).first()
    if not sender or not recipient:
        raise HTTPException(status_code=404, detail="User not found")
    if sender.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    sender_transaction = Transaction(
        user_id=sender.id,
        transaction_type="TRANSFER_OUT",
        amount=transfer.amount,
        description=transfer.description
    )
    db.add(sender_transaction)
    db.commit()
    db.refresh(sender_transaction)
    recipient_transaction = Transaction(
        user_id=recipient.id,
        transaction_type="TRANSFER_IN",
        amount=transfer.amount,
        description=transfer.description
    )
    db.add(recipient_transaction)
    db.commit()
    db.refresh(recipient_transaction)
    sender.balance -= transfer.amount
    recipient.balance += transfer.amount
    db.commit()
    return {
        "transfer_id": "unique_transfer_id",
        "sender_transaction_id": sender_transaction.id,
        "recipient_transaction_id": recipient_transaction.id,
        "amount": transfer.amount,
        "sender_new_balance": sender.balance,
        "recipient_new_balance": recipient.balance,
        "status": "completed"
    }



@app.get("/transfer/{transfer_id}")
def get_transfer(transfer_id: str, db: Session = Depends(get_db)):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer

