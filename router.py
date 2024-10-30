from fastapi import APIRouter, HTTPException
from models import EmployeeCreate, Employee,Customer,CustomerCreate
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

@router.post("/employees", response_model=Employee)
def create_employee(employee: EmployeeCreate):
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

@router.get("/recent-orders/customers")
def get_recent_orders_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT c.customer_id, c.name 
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
        """
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return {"message": "No recent orders found."}
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/employees/stats/")
def get_employee_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                MAX(employee_id) AS max_employee_id,
                MIN(employee_id) AS min_employee_id,
                AVG(employee_id) AS average_employee_id
            FROM employees;
        """)
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="No employees found")
        
        result['average_employee_id'] = float(result['average_employee_id'])
        
        return {
            "max_employee_id": result['max_employee_id'],
            "min_employee_id": result['min_employee_id'],
            "average_employee_id": result['average_employee_id']
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        cursor.close()
        connection.close()

@router.get("/employees/count_chefs")
def count_chefs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT COUNT(*) AS total_chefs
            FROM employees
            WHERE position = 'Chef';
        """
        cursor.execute(query)
        result = cursor.fetchone()

        
        if result is None or result['total_chefs'] is None:
            raise HTTPException(status_code=404, detail="No chefs found")

        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@router.get("/employees/orders", response_model=List[EmployeeCreate])
def get_employees_with_orders():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        query = """
        SELECT 
            e.employee_id, e.name, e.position, e.email, e.phone,
            o.order_id, o.order_date
        FROM employees e
        JOIN orders o ON e.employee_id = o.employee_id
        """
        cursor.execute(query)
        result = cursor.fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="No orders found for employees")
        
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        cursor.close()
        connection.close()