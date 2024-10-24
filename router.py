from fastapi import APIRouter, HTTPException
from models import CustomerCreate, Customer
from database import get_db_connection
from typing import List
import mysql.connector

router = APIRouter()

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

@router.post("/customers/bulk/", response_model=List[Customer])
def create_customers_bulk(customers: List[CustomerCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        created_customers = []
        for customer in customers:
            query = """
            INSERT INTO customers (name, email, phone)
            VALUES (%s, %s, %s)
            """
            values = (customer.name, customer.email, customer.phone)
            
            cursor.execute(query, values)
            new_customer_id = cursor.lastrowid
            created_customers.append(Customer(customer_id=new_customer_id, **customer.dict()))
        
        conn.commit()
        return created_customers
    except mysql.connector.Error as e:
        conn.rollback()
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
