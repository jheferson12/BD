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
        created_employees = []
        for employee in employees:
            query = """
            INSERT INTO employees (name, position, email, phone)
            VALUES (%s, %s, %s, %s)
            """
            values = (employee.name, employee.position, employee.email, employee.phone)
            
            cursor.executemany(query, values)
            new_employee_id = cursor.lastrowid
            created_employees.append(Employee(employee_id=new_employee_id, **employee.dict()))
        
        conn.commit()
        return created_employees
    except mysql.connector.Error as e:
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


@router.get("/employees/", response_model=List[Employee])
def get_employees():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT e.employee_id, e.name, d.department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            ORDER BY e.employee_id;
        """)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        connection.close()

@router.get("/employees/stats/", response_model=Employee)
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
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        connection.close()

@router.get("/employees/", response_model=List[Employee])
def get_all_employees():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT employee_id, name, position, email, phone
            FROM employees
            ORDER BY name;
        """)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        connection.close()