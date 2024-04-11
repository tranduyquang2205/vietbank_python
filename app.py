from vietbank import VietBank
import json
import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


app = FastAPI()
vietbank = VietBank()

class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
@app.post('/login', tags=["login"])
def login_api(input: LoginDetails):
        session_raw = vietbank.login(input.username, input.password)
        return session_raw
    

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
        balance = vietbank.get_balance(input.account_number)
        return balance
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    to_date: str
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
        history = vietbank.get_transactions(input.account_number,input.from_date,input.to_date)
        return history


if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)
    
    