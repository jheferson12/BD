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
        created_uploads = []

        query = """
        INSERT INTO uploadmenu (menu_id, upload_date)
        VALUES (%s, %s)
        """

        for upload in uploads:
            values = (upload.menu_id, upload.upload_date)
            cursor.execute(query, values)

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

