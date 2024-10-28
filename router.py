from fastapi import APIRouter, HTTPException
from models import UploadCreate, Upload
from database import get_db_connection
from typing import List
import mysql.connector

router = APIRouter()

@router.get("/uploadmenu/", response_model=List[Upload])
def list_uploads():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM uploadmenu"
        cursor.execute(query)
        uploads = cursor.fetchall()
        return [Upload(**upload) for upload in uploads]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/uploadmenu/", response_model=Upload)
def create_upload(upload: UploadCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        INSERT INTO uploadmenu (menu_id, upload_date)
        VALUES (%s, %s)
        """
        values = (upload.menu_id, upload.upload_date)

        cursor.executemany(query, values)
        conn.commit()

        new_upload_id = cursor.lastrowid
        return Upload(upload_id=new_upload_id, **upload.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/uploadmenu/bulk/", response_model=List[Upload])
def create_uploads_bulk(uploads: List[UploadCreate]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        created_uploads = []

        query = """
        INSERT INTO uploadmenu (menu_id, upload_date)
        VALUES (%s, %s)
        """

        for upload in uploads:
            values = (upload.menu_id, upload.upload_date)
            cursor.executemany(query, values)

            new_upload_id = cursor.lastrowid
            created_uploads.append(
                Upload(upload_id=new_upload_id, **upload.dict())
            )

        conn.commit()
        return created_uploads

    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/uploadmenu/{upload_id}", response_model=dict)
def delete_upload(upload_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM uploadmenu WHERE upload_id = %s", (upload_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Upload not found")

        query = "DELETE FROM uploadmenu WHERE upload_id = %s"
        cursor.execute(query, (upload_id,))
        conn.commit()

        return {"message": f"Upload with ID {upload_id} successfully deleted"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.get("/products/total_sales", response_model=List[dict])
def get_product_sales():
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    query = """
    SELECT p.product_id, p.name AS product_name, 
           SUM(od.quantity * od.price) AS total_sales
    FROM order_details od
    JOIN products p ON od.product_id = p.product_id
    GROUP BY p.product_id;
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    
    cursor.close()
    conn.close()
    
    return result

@router.get("/menu/average_price", response_model=List[dict])
def get_average_price_per_category():
   
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    query = """
    SELECT mc.category_name, AVG(um.price) AS average_price
    FROM uploadmenu um
    JOIN menu_categories mc ON um.category_id = mc.category_id
    GROUP BY mc.category_name;
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    
    cursor.close()
    conn.close()
    
    return result

@router.get("/uploadmenu/unordered", response_model=List[dict])
def get_unordered_menus():
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    query = """
    SELECT um.uploadmenu_id, um.name
    FROM uploadmenu um
    LEFT JOIN order_items oi ON um.uploadmenu_id = oi.menu_id
    WHERE oi.menu_id IS NULL;
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
   
    cursor.close()
    conn.close()
    
    return result