from fastapi import APIRouter, HTTPException
from models import OrderCreate, Order  
from database import get_db_connection
from typing import List
import mysql.connector

router = APIRouter()

@router.post("/orders/", response_model=Order)  
def create_order(order: OrderCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO orders (customer_id, employee_id, order_date)
        VALUES (%s, %s, %s)
        """
        values = (order.customer_id, order.employee_id, order.order_date)

        cursor.execute(query, values)
        conn.commit()

        new_order_id = cursor.lastrowid

        return Order(order_id=new_order_id, **order.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/orders/bulk/", response_model=List[Order])
def create_orders_bulk(orders: List[OrderCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO orders (customer_id, employee_id, order_date)
        VALUES (%s, %s, %s)
        """
        values = [(order.customer_id, order.employee_id, order.order_date) for order in orders]

        cursor.executemany(query, values)
        new_order_id_start = cursor.lastrowid
        conn.commit()

        created_orders = []
        for i, order in enumerate(orders):
            created_orders.append(Order(order_id=new_order_id_start + i, **order.dict()))

        return created_orders
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/orders/", response_model=List[Order]) 
def list_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM orders"
        cursor.execute(query)
        orders = cursor.fetchall()
        return [Order(**order) for order in orders]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/orders/{order_id}", response_model=dict)  
def delete_order(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "DELETE FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")

        conn.commit()
        return {"message": f"Order with ID {order_id} successfully deleted"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


