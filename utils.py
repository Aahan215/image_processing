import pandas as pd
from fastapi import HTTPException

def validate_csv(df: pd.DataFrame):
    required_columns = ["Serial Number", "Product Name", "Input Image Urls"]
    for col in required_columns:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

def upload_to_storage(output_image):
    # Implement the function to upload to cloud storage (e.g., S3) and return the URL
    return "https://storage-url-for-output-image.jpg"
