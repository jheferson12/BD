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
            
            cursor.execute(query, values)
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
