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
            cursor.executemany(query, values)

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



@router.get("/order_details")
def get_order_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT od.order_detail_id, o.order_id, p.product_id, p.name AS product_name, od.quantity, od.price
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    JOIN products p ON od.product_id = p.product_id;
    """

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    return result

@router.get("/order_details/min_max")

def get_min_max_order_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        MIN(order_detail_id) AS min_order_detail_id,
        MAX(order_detail_id) AS max_order_detail_id,
        MIN(quantity) AS min_quantity,
        MAX(quantity) AS max_quantity
    FROM order_details;
    """

    cursor.execute(query)
    result = cursor.fetchone()  # Usar fetchone ya que solo hay un registro
    cursor.close()
    conn.close()

    return {
        "min_order_detail_id": result['min_order_detail_id'],
        "max_order_detail_id": result['max_order_detail_id'],
        "min_quantity": result['min_quantity'],
        "max_quantity": result['max_quantity'],
    }

@router.get("/products/quantity_last_month")
def get_product_quantity_last_month():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT p.product_id, p.name AS product_name, SUM(od.quantity) AS total_quantity
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    JOIN products p ON od.product_id = p.product_id
    WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
    GROUP BY p.product_id
    ORDER BY total_quantity DESC;
    """

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    return result