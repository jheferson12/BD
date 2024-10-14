from pydantic import BaseModel, Field

class EmployeeCreate(BaseModel):
    employee_id: int = Field(..., description="ID del empleado", example=1)
    name: str = Field(..., description="Nombre del empleado", example="John Doe")
    position: str = Field(..., description="Cargo del empleado", example="Gerente de Ventas")
    email: str = Field(..., description="Correo del empleado", example="johndoe@example.com")
    phone: str = Field(..., description="Teléfono del empleado", example="+1234567890")

class Employee(EmployeeCreate):
    employee_id: int = Field(..., description="ID del empleado", example=1)





