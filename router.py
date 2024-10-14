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
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/customers/", response_model=Customer)
def create_customer(customer: CustomerCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        INSERT INTO customers (customer_id, name, email, phone)
        VALUES (%s, %s, %s, %s)
        """
        values = (customer.customer_id, customer.name, customer.email, customer.phone)
        
        cursor.execute(query, values)
        conn.commit()
        
        return Customer(**customer.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/customers/{customer_id}/bulk/", response_model=List[Customer])
def create_customers_bulk(customer_id: int, customers: List[CustomerCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar si el cliente principal existe
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cliente principal no encontrado")
        
        created_customers = []
        for customer in customers:
            query = """
            INSERT INTO customers (customer_id, name, email, phone)
            VALUES (%s, %s, %s, %s)
            """
            values = (customer.customer_id, customer.name, customer.email, customer.phone)
            
            cursor.execute(query, values)
            created_customers.append(Customer(**customer.dict()))
        
        conn.commit()
        return created_customers
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

