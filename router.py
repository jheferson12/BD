from fastapi import APIRouter, HTTPException
from models import EmployeeCreate, Employee,Customer,CustomerCreate,OrderCreate,Order,MenuCreate, Menu
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
        query = """
        INSERT INTO order_details (order_id, menu_id, quantity)
        VALUES (%s, %s, %s)
        """
        
        values = [(detail.order_id, detail.menu_id, detail.quantity) for detail in order_details]
        cursor.executemany(query, values)
        conn.commit()

        new_order_detail_ids = cursor.lastrowid - len(order_details) + 1
        created_order_details = [
            OrderDetail(order_detail_id=new_order_detail_ids + i, **detail.dict())
            for i, detail in enumerate(order_details)
        ]

        return created_order_details

    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

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

@router.post("/menus/", response_model=Menu)
def create_menu(menu: MenuCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO menus (name, description, price)
        VALUES (%s, %s, %s)
        """
        values = (menu.name, menu.description, menu.price)

        cursor.execute(query, values)
        conn.commit()

        new_menu_id = cursor.lastrowid

        return Menu(menu_id=new_menu_id, **menu.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


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
        conn.commit()

        created_customers = [
            Customer(customer_id=cursor.lastrowid + i, **customer.dict())
            for i, customer in enumerate(customers)
        ]
        
        return created_customers
    except mysql.connector.Error as e:
        conn.rollback()
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

@router.post("/menus/bulk/", response_model=List[Menu])
def create_menus_bulk(menus: List[MenuCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO menus (name, description, price)
        VALUES (%s, %s, %s)
        """
        values = [(menu.name, menu.description, menu.price) for menu in menus]

        cursor.executemany(query, values)
        new_menu_id_start = cursor.lastrowid
        conn.commit()

        created_menus = []
        for i, menu in enumerate(menus):
            created_menus.append(Menu(menu_id=new_menu_id_start + i, **menu.dict()))

        return created_menus
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
        query = """
        INSERT INTO orders (customer_id, employee_id, order_date)
        VALUES (%s, %s, %s)
        """
        values = (Order.customer_id, Order.employee_id, Order.order_date)

        cursor.execute(query, values)
        conn.commit()

        new_order_id = cursor.lastrowid

        return Order(order_id=new_order_id, **Order.dict())
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

@router.get("/menus/", response_model=List[Menu])
def list_menus():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM menus"
        cursor.execute(query)
        menus = cursor.fetchall()
        return [Menu(**menu) for menu in menus]
    except mysql.connector.Error as e:
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

@router.delete("/menus/{menu_id}", response_model=dict)
def delete_menu(menu_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "DELETE FROM menus WHERE menu_id = %s"
        cursor.execute(query, (menu_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Menu not found")

        conn.commit()
        return {"message": f"Menu with ID {menu_id} successfully deleted"}
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

@router.get("/customers/total-sales", response_model=List[dict])
def get_customers_total_sales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT c.customer_id, c.name AS customer_name, SUM(od.quantity) AS total_sales
        FROM orders o
        JOIN order_details od ON o.order_id = od.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id
        """
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            raise HTTPException(status_code=404, detail="No data found")
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/products/total-quantity", response_model=List[dict])
def get_products_total_quantity():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT od.menu_id, SUM(od.quantity) AS total_quantity
        FROM order_details od
        JOIN orders o ON od.order_id = o.order_id
        WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
        GROUP BY od.menu_id
        ORDER BY total_quantity DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            raise HTTPException(status_code=404, detail="No data found")
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

@router.get("/menus/not_ordered")
def get_menus_not_ordered():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT m.menu_id, m.name
        FROM menus m
        LEFT JOIN order_details od ON m.menu_id = od.menu_id
        WHERE od.menu_id IS NULL;
        """
        cursor.execute(query)
        result = cursor.fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="No menus found")
        
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/menus/min_max_price")
def get_min_max_price():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        MIN(price) AS min_price, 
        MAX(price) AS max_price 
    FROM menus;
    """
    
    cursor.execute(query)
    result = cursor.fetchone()  
    cursor.close()
    conn.close()
    
    return {
        "min_price": result["min_price"] if result else None,
        "max_price": result["max_price"] if result else None
    }

@router.get("/menus/average_price", response_model=List[float])
def get_average_price():
    conn = get_db_connection()
    cursor = conn.cursor()    
    try:
        
        query = """
        SELECT AVG(price) AS average_price
        FROM menus;
        """
        
        cursor.execute(query)
        result = cursor.fetchone() 
        
        return [result[0]] if result[0] is not None else [0.0]
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()
