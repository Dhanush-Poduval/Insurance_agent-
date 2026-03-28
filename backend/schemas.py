from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Signup(BaseModel):
    name:str
    email:str
    password:str
    company:str
    current_delivery_location : str

class ShowUser(BaseModel):
    id:int
    name:str
    email:str
    class Config():
        orm_mode=True
class risk(BaseModel):
    id:int
    name:str
    risk:int
    class Config():
        orm_mode=True
