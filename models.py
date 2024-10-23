from pydantic import BaseModel, Field

class CustomerCreate(BaseModel):
    """
    Modelo para la creación de un cliente. 
    Define los campos requeridos al crear un cliente en la base de datos.
    """
    name: str = Field(..., description="Nombre del cliente")
    email: str = Field(..., description="Correo del cliente")
    phone: str = Field(..., description="Teléfono del cliente")

class Customer(CustomerCreate):
    """
    Modelo que extiende CustomerCreate y representa un cliente ya creado.
    Incluye los mismos campos que CustomerCreate, más el ID autogenerado.
    """
    customer_id: int = Field(..., description="ID del cliente (autogenerado)")

    class Config:
        from_attributes = True



 # 



