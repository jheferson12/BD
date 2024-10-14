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
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/employees/", response_model=Employee)
def create_employee(employee: EmployeeCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        INSERT INTO employees (employee_id, name, position, email, phone)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (employee.employee_id, employee.name, employee.position, employee.email, employee.phone)
        
        cursor.execute(query, values)
        conn.commit()
        
        return Employee(**employee.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/employees/{employee_id}/bulk/", response_model=List[Employee])
def create_employees_bulk(employee_id: int, employees: List[EmployeeCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar si el cliente principal existe
        cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Empleado principal no encontrado")
        
        created_employees = []
        for employee in employees:
            query = """
            INSERT INTO employees (employee_id, name, position, email, phone)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (employee.employee_id, employee.name, employee.position, employee.email, employee.phone)
            
            cursor.execute(query, values)
            created_employees.append(Employee(**employee.dict()))
        
        conn.commit()
        return created_employees
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

