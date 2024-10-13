from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import uuid4
import pandas as pd
import os
from tasks import process_images_task
from database import SessionLocal, engine
from models import Request, Product
from utils import validate_csv

app = FastAPI()

@app.post("/api/upload")
async def upload_csv(file: UploadFile):
    # Validate the file format
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV files are accepted.")

    # Read and validate CSV data
    try:
        df = pd.read_csv(file.file)
        validate_csv(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV validation error: {e}")

    # Generate unique request ID
    request_id = str(uuid4())

    # Store the initial request data in the database
    db = SessionLocal()
    new_request = Request(id=request_id, status="Pending")
    db.add(new_request)
    db.commit()

    # Store product information
    for _, row in df.iterrows():
        product = Product(
            request_id=request_id,
            product_name=row['Product Name'],
            input_urls=row['Input Image Urls'].split(',')
        )
        db.add(product)
    db.commit()
    db.close()

    # Trigger asynchronous image processing
    process_images_task.delay(request_id)

    return {"request_id": request_id}

@app.get("/api/status/{request_id}")
async def check_status(request_id: str):
    db = SessionLocal()
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request ID not found")

    response = {
        "request_id": request_id,
        "status": request.status,
        "products": [
            {
                "product_name": product.product_name,
                "input_urls": product.input_urls,
                "output_urls": product.output_urls
            }
            for product in request.products
        ]
    }

    db.close()
    return response
