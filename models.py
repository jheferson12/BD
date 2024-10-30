from pydantic import BaseModel, Field
from typing import Optional

class CustomerCreate(BaseModel):
       
    name: str = Field(..., description="Nombre del cliente")
    email: str = Field(..., description="Correo del cliente")
    phone: str = Field(..., description="Teléfono del cliente")

class Customer(CustomerCreate):
   
    customer_id: int = Field(..., description="ID del cliente") 


class EmployeeCreate(BaseModel):
    name: str = Field(..., description="Employee's name")
    position: str = Field(..., description="Employee's position")
    email: str = Field(..., description="Employee's email")
    phone: str = Field(..., description="Employee's phone")

class Employee(EmployeeCreate):
    employee_id: Optional[int] = Field(None, description="Employee ID")

    class Config:
        from_attributes = True


