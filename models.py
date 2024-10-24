from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrderCreate(BaseModel):
    customer_id: Optional[int] = None  
    employee_id: Optional[int] = None  
    order_date: datetime  

class Order(OrderCreate):
    order_id: int  



