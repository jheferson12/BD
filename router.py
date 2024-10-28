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


@router.get("/orders/customers")
def get_orders_with_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    
    query = """
    SELECT o.order_id, o.order_date, c.customer_id, c.name AS customer_name
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return result

@router.get("/customers/total-sales")
def get_customers_total_sales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    
    query = """
    SELECT c.customer_id, c.name AS customer_name, SUM(oi.quantity * oi.price) AS total_sales
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return result

@router.get("/products/total-quantity")
def get_products_total_quantity():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

   
    query = """
    SELECT p.product_id, p.name AS product_name, SUM(oi.quantity) AS total_quantity
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
    GROUP BY p.product_id
    ORDER BY total_quantity DESC
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return result

@router.get("/customers/stats")
def get_customer_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

   
    query = """
    SELECT 
        MAX(customer_id) AS max_id,
        MIN(customer_id) AS min_id,
        AVG(customer_id) AS avg_id
    FROM 
        customers;
    """
    
    cursor.execute(query)
    stats = cursor.fetchone()  
    cursor.close()
    conn.close()
    
    return {
        "max_id": stats['max_id'],
        "min_id": stats['min_id'],
        "avg_id": stats['avg_id']
    }