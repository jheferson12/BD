from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class MenuCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal

class Menu(MenuCreate):
    menu_id: int



