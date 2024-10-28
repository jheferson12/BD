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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/menus/", response_model=Menu)
def create_menu(menu: MenuCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO menus (name, description, price)
        VALUES (%s, %s, %s)
        """
        values = (menu.name, menu.description, menu.price)

        cursor.execute(query, values)
        conn.commit()

        new_menu_id = cursor.lastrowid

        return Menu(menu_id=new_menu_id, **menu.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
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
            raise HTTPException(status_code=404, detail="Menu not found")

        conn.commit()
        return {"message": f"Menu with ID {menu_id} successfully deleted"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.get("/menus/not_ordered")
def get_menus_not_ordered():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT m.menu_id, m.name
    FROM menus m
    LEFT JOIN order_items oi ON m.menu_id = oi.menu_id
    WHERE oi.menu_id IS NULL;
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return result

@router.get("/menus/min_max_price")
def get_min_max_price():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        MIN(price) AS min_price, 
        MAX(price) AS max_price 
    FROM menus;
    """
    
    cursor.execute(query)
    result = cursor.fetchone()  
    cursor.close()
    conn.close()
    
    return {
        "min_price": result["min_price"] if result else None,
        "max_price": result["max_price"] if result else None
    }

@router.get("/menus/average_price")
def get_average_price_per_category():
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT category, AVG(price) AS average_price
    FROM menus
    GROUP BY category;
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return result