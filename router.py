from fastapi import APIRouter, HTTPException
from models import OrderDetailCreate, OrderDetail
from database import get_db_connection
from typing import List
import mysql.connector

router = APIRouter()

@router.get("/order_details/", response_model=List[OrderDetail])
def list_order_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM order_details"
        cursor.execute(query)
        order_details = cursor.fetchall()
        return [OrderDetail(**detail) for detail in order_details]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/order_details/", response_model=OrderDetail)
def create_order_detail(order_detail: OrderDetailCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO order_details (order_id, menu_id, quantity)
        VALUES (%s, %s, %s)
        """
        values = (order_detail.order_id, order_detail.menu_id, order_detail.quantity)

        cursor.execute(query, values)
        conn.commit()

        new_order_detail_id = cursor.lastrowid
        return OrderDetail(order_detail_id=new_order_detail_id, **order_detail.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/order_details/bulk/", response_model=List[OrderDetail])
def create_order_details_bulk(order_details: List[OrderDetailCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        created_order_details = []

        query = """
        INSERT INTO order_details (order_id, menu_id, quantity)
        VALUES (%s, %s, %s)
        """
        
        for detail in order_details:
            values = (detail.order_id, detail.menu_id, detail.quantity)
            cursor.execute(query, values)

            new_order_detail_id = cursor.lastrowid
            created_order_details.append(
                OrderDetail(order_detail_id=new_order_detail_id, **detail.dict())
            )

        conn.commit()
        return created_order_details

    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        
@router.delete("/order_details/{order_detail_id}", response_model=dict)
def delete_order_detail(order_detail_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM order_details WHERE order_detail_id = %s", (order_detail_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Order detail not found")

        query = "DELETE FROM order_details WHERE order_detail_id = %s"
        cursor.execute(query, (order_detail_id,))
        conn.commit()

        return {"message": f"Order detail with ID {order_detail_id} successfully deleted"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

