from pydantic import BaseModel, Field
from typing import Optional

class EmployeeCreate(BaseModel):
    name: str = Field(..., description="Nombre del empleado")
    position: str = Field(..., description="Cargo del empleado")
    email: str = Field(..., description="Correo del empleado")
    phone: str = Field(..., description="Teléfono del empleado")

class Employee(EmployeeCreate):
    employee_id: Optional[int] = Field(None, description="ID del empleado")

    class Config:
        from_attributes = True



