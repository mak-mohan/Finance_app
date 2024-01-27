# from fastapi import FastAPI, HTTPException, Depends,status
# from typing import Annotated,List
# from sqlalchemy.orm import Session
# from pydantic import BaseModel, Field
# from database import SessionLocal, engine
# import models
# from fastapi.middleware.cors import CORSMiddleware

# app= FastAPI()

# origins ={
#     'http://localhost:3000'
# }

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# class TransactionBase(BaseModel):
#     amount: int
#     category : str = Field(min_length=2,max_length=5)
#     description:str
#     is_income:bool
#     date:str

# class TransactionModel(TransactionBase):
#    id: int 

#    class Config:
#        orm_mode= True


# def get_db():
#     db= SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# db_dependency = Annotated[Session, Depends(get_db)]

# models.Base.metadata.create_all(bind=engine)

# @app.post("/transactions/", response_model=TransactionModel, status_code=status.HTTP_201_CREATED)
# async def create_transaction(transaction: TransactionBase,db: db_dependency):
#     try:
#         print(transaction)      
#         db_transaction = models.Transaction(**transaction.model_dump())
#         db.add(db_transaction)
#         db.commit()
#         db.refresh(db_transaction)
#         create_transaction=TransactionModel('id',category=transaction.category)
#     except Exception as e:
#         print(e)
    

# @app.get("/transactions/", response_model=List[TransactionModel])
# async def read_transactions(db: db_dependency,  skip:int=0,limit: int=100):
#     transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
#     print(transactions)
#     return transactions



from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = {
    'http://localhost:3000'
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class TransactionBase(BaseModel):
    amount: int
    category: str = Field(min_length=2, max_length=5)
    description: str
    is_income: bool
    date: str

    @validator("amount")
    def validate_amount(cls, value):
        if not isinstance(value, int):
            raise ValueError("Amount must be an integer")
        return value

class TransactionModel(TransactionBase):
    id: int

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


models.Base.metadata.create_all(bind=engine)

@app.post("/transactions/", response_model=TransactionModel, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionBase, db: db_dependency):
    try:
        db_transaction = models.Transaction(**transaction.dict())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction  # Return the created transaction
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/transactions/", response_model=List[TransactionModel])
async def read_transactions(db: db_dependency, skip: int = 0, limit: int = 100):
    transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
    return transactions

