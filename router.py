from fastapi import APIRouter, HTTPException
from models import EmployeeCreate, Employee
from database import get_db_connection
from typing import List
import mysql.connector

router = APIRouter()

@router.get("/employees/", response_model=List[Employee])
def list_employees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM employees"
        cursor.execute(query)
        employees = cursor.fetchall()
        return [Employee(**employee) for employee in employees]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/employees/bulk/", response_model=List[Employee])
def create_employees_bulk(employees: List[EmployeeCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
       
        query = """
        INSERT INTO employees (name, position, email, phone)
        VALUES (%s, %s, %s, %s)
        """        
        values = [
            (employee.name, employee.position, employee.email, employee.phone)
            for employee in employees
        ]        
        cursor.executemany(query, values)        
        conn.commit()
        created_employees = [
            Employee(employee_id=cursor.lastrowid + i, **employee.dict())
            for i, employee in enumerate(employees)
        ]
        return created_employees

    except MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cursor.close()
        conn.close()

@router.post("/employees", response_model=Employee)
def create_employee(employee: EmployeeCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO employees (name, position, email, phone)
        VALUES (%s, %s, %s, %s)
        """
        values = (employee.name, employee.position, employee.email, employee.phone)
        
        cursor.execute(query, values)
        conn.commit()

        new_employee_id = cursor.lastrowid

        return Employee(employee_id=new_employee_id, **employee.dict())

    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/employees/{employee_id}", response_model=dict)
def delete_employee(employee_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Employee not found")
        
        query = "DELETE FROM employees WHERE employee_id = %s"
        cursor.execute(query, (employee_id,))
        conn.commit()
        
        return {"message": f"Employee with ID {employee_id} successfully deleted"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
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

@router.get("/employees/orders", response_model=List[Employee])
def get_employees_with_orders():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                e.employee_id, e.name AS employee_name, e.position, 
                o.order_id, o.order_date, o.total_amount
            FROM employees e
            JOIN orders o ON e.employee_id = o.employee_id;
        """
        cursor.execute(query)
        result = cursor.fetchall()

        
        if not result:
            raise HTTPException(status_code=404, detail="No orders found for employees")

        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()