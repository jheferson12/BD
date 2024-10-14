from pydantic import BaseModel, Field

# este seria la parte de customers-------------------------------------------------------------------
class CustomerCreate(BaseModel):
    """
    Modelo para la creación de un cliente. 
    Define los campos requeridos al crear un cliente en la base de datos.
    """
    customer_id: int = Field(..., description="ID del cliente", example=1)
    name: str = Field(..., description="Nombre del cliente", example="John Doe")
    email: str = Field(..., description="Correo del cliente", example="johndoe@example.com")
    phone: str = Field(..., description="Teléfono del cliente", example="+1234567890")

class Customer(CustomerCreate):
    """
    Modelo que extiende CustomerCreate y representa un cliente ya creado.
    Incluye los mismos campos, pero puede usarse para respuestas de la API.
    """
    customer_id: int = Field(..., description="ID del cliente", example=1)



 # 
# aqui se acaba la parte de customers
# --------------------------------------------------------------------------------------------------


