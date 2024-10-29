from fastapi import APIRouter, HTTPException
from models import CustomerCreate, Customer
from database import get_db_connection
from typing import List
import mysql.connector

router = APIRouter()


@router.post("/customers/bulk/", response_model=List[Customer])
def create_customers_bulk(customers: List[CustomerCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        INSERT INTO customers (name, email, phone)
        VALUES (%s, %s, %s)
        """ 
       
        values = [(customer.name, customer.email, customer.phone) for customer in customers]        
        
        cursor.executemany(query, values)      
        
        created_customers = []
        for i in range(cursor.rowcount):
            new_customer_id = cursor.lastrowid - cursor.rowcount + 1 + i
            created_customers.append(Customer(customer_id=new_customer_id, **customers[i].dict()))
        
        conn.commit()
        return created_customers
    
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

@router.post("/customers/", response_model=Customer)
def create_customer(customer: CustomerCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        
        query = """
        INSERT INTO customers (name, email, phone)
        VALUES (%s, %s, %s)
        """
        values = (customer.name, customer.email, customer.phone)
        
        cursor.execute(query, values)
        conn.commit()
        
        new_customer_id = cursor.lastrowid
        
        return Customer(customer_id=new_customer_id, **customer.dict())

    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cursor.close()
        conn.close()

@router.get("/customers/", response_model=List[Customer])
def list_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM customers"
        cursor.execute(query)
        customers = cursor.fetchall()
        return [Customer(**customer) for customer in customers]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/customers/{customer_id}", response_model=dict)
def delete_customer(customer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Customer not found")
        
        query = "DELETE FROM customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        conn.commit()
        
        return {"message": f"Customer with ID {customer_id} successfully deleted"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/customers")
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()    
    max_customer = max(customers, key=lambda x: x['customer_id']) if customers else None    
    if max_customer:
        customers.remove(max_customer)   
    if max_customer:
        max_customer_message = f"You're the best customer, {max_customer['name']}!"
    else:
        max_customer_message = "No customers available."

    return {
        "customers": customers,
        "max_customer_message": max_customer_message,
        "max_customer": max_customer
    }

@router.get("/customers/stats")
def get_customers_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

   
    query = """
    SELECT 
        MAX(customer_id) AS max_id,
        MIN(customer_id) AS min_id,
        AVG(customer_id) AS avg_id
    FROM customers
    """
    
    cursor.execute(query)
    stats = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "max_id": stats["max_id"],
        "min_id": stats["min_id"],
        "avg_id": stats["avg_id"],
    }

@router.get("/customers/{customer_id}")
def get_customer_by_id(customer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM customers WHERE customer_id = %s"
    cursor.execute(query, (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()  
    
    return customer

@router.get("/customers/orders")
def get_customers_with_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
   
    query = """
    SELECT c.customer_id, c.name, SUM(od.quantity) AS total_items_ordered 
    FROM customers c 
    JOIN orders o ON c.customer_id = o.customer_id 
    JOIN order_details od ON o.order_id = od.order_id 
    GROUP BY c.customer_id 
    ORDER BY total_items_ordered DESC 
    LIMIT 1;
    """
    
    cursor.execute(query)
    result = cursor.fetchone()  
    cursor.close()
    conn.close()
    
    return result if result else {"message": "No orders found."}  

