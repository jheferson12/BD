from fastapi import APIRouter, HTTPException
from models import MenuCreate, Menu
from database import get_db_connection
from typing import List
import mysql.connector

router = APIRouter()

@router.post("/menus/bulk/", response_model=List[Menu])
def create_menus_bulk(menus: List[MenuCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        INSERT INTO menus (name, description, price)
        VALUES (%s, %s, %s)
        """
        values = [(menu.name, menu.description, menu.price) for menu in menus]
        
        cursor.executemany(query, values)
        new_menu_id_start = cursor.lastrowid
        conn.commit()
        
        created_menus = []
        for i, menu in enumerate(menus):
            created_menus.append(Menu(menu_id=new_menu_id_start + i, **menu.dict()))
        
        return created_menus
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/menus/", response_model=List[Menu])
def list_menus():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM menus"
        cursor.execute(query)
        menus = cursor.fetchall()
        return [Menu(**menu) for menu in menus]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/menus/{menu_id}", response_model=dict)
def delete_menu(menu_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "DELETE FROM menus WHERE menu_id = %s"
        cursor.execute(query, (menu_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
        conn.commit()
        return {"message": f"Menú con ID {menu_id} eliminado exitosamente"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

