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

        cursor.execute(query, values)
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
        query = """INSERT INTO uploadmenu (menu_id, upload_date) VALUES (%s, %s)"""
        values = [(upload.menu_id, upload.upload_date) for upload in uploads]
        
        cursor.executemany(query, values)
        first_upload_id = cursor.lastrowid

        created_uploads = [
            Upload(upload_id=first_upload_id + i, **upload.dict())
            for i, upload in enumerate(uploads)
        ]

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

@router.get("/menus/not_ordered", response_model=List[dict])
def get_menus_not_ordered():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT m.menu_id, m.name
        FROM menus m
        WHERE m.menu_id NOT IN (
            SELECT menu_id
            FROM order_details
        );
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
@router.get("/menu/upload_count", response_model=List[dict])
def get_upload_count_per_menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT menu_id, COUNT(*) AS upload_count
        FROM uploadmenu
        GROUP BY menu_id;
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

@router.get("/uploadmenu/unordered", response_model=List[dict])
def get_unordered_menus():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT um.upload_id, um.menu_id
        FROM uploadmenu um
        LEFT JOIN order_details od ON um.menu_id = od.menu_id
        WHERE od.menu_id IS NULL;
        """
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No unordered menus found")

        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        cursor.close()
        conn.close()