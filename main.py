from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from database import engine,get_db,Base
from models import User,Transactions
from schemas import UserSchema,TransactionSchema,TransferSchema,TransactionResponseSchema


Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/users/", response_model=UserSchema)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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


@app.get("/transactions/{user_id}")
def get_transaction_history(user_id: int, db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = db.query(Transactions).filter(Transactions.user_id == user_id).offset((page - 1) * limit).limit(limit).all()
    total = db.query(Transactions).filter(Transactions.user_id == user_id).count()
    
    transaction_list = []
    for transaction in transactions:
        transaction_list.append({
            "transaction_id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "amount": float(transaction.amount),
            "description": transaction.description,
            "created_at": transaction.created_at
        })
    
    return {
        "transactions": transaction_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/transactions/detail/{transaction_id}")
def get_transaction_detail(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transactions).filter(Transactions.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "transaction_id": transaction.id,
        "user_id": transaction.user_id,
        "transaction_type": transaction.transaction_type,
        "amount": float(transaction.amount),
        "description": transaction.description,
        "recipient_user_id": transaction.recipient_id,
        "reference_transaction_id": transaction.reference_transaction_id,
        "created_at": transaction.created_at
    }

@app.post("/transactions")
def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    # Validate transaction type
    valid_types = ["CREDIT", "DEBIT", "TRANSFER_IN", "TRANSFER_OUT"]
    if transaction.transaction_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid transaction type. Must be one of: {valid_types}")
    
    # Validate user exists
    user = db.query(User).filter(User.id == transaction.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # For DEBIT transactions, check sufficient balance
    if transaction.transaction_type == "DEBIT" and user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create transaction record
    db_transaction = Transactions(
        user_id=transaction.user_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
        reference_transaction_id=transaction.reference_transaction_id,
        recipient_id=transaction.recipient_user_id
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return {
        "transaction_id": db_transaction.id,
        "user_id": db_transaction.user_id,
        "transaction_type": db_transaction.transaction_type,
        "amount": float(db_transaction.amount),
        "description": db_transaction.description,
        "created_at": db_transaction.created_at
    }


@app.get("/transfer/{transfer_id}")
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    # Get the TRANSFER_OUT transaction (which represents the transfer)
    transfer_out = db.query(Transactions).filter(
        Transactions.id == transfer_id,
        Transactions.transaction_type == "TRANSFER_OUT"
    ).first()
    
    if not transfer_out:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    # Find the corresponding TRANSFER_IN transaction
    transfer_in = db.query(Transactions).filter(
        Transactions.reference_transaction_id == transfer_id,
        Transactions.transaction_type == "TRANSFER_IN"
    ).first()
    
    return {
        "transfer_id": f"transfer_{transfer_out.id}",
        "sender_user_id": transfer_out.user_id,
        "recipient_user_id": transfer_out.recipient_id,
        "amount": float(transfer_out.amount),
        "description": transfer_out.description,
        "status": "completed",
        "created_at": transfer_out.created_at
    }



