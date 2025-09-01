from fastapi import FastAPI
from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from database import engine,get_db,Base
from models import User,Transactions
from schemas import UserSchema,TransactionSchema

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/users", response_model=UserSchema)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=list[UserSchema])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/transactions", response_model=list[TransactionSchema])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(Transactions).offset(skip).limit(limit).all()
    return transactions
