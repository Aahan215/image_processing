import requests
from PIL import Image
from io import BytesIO
from database import SessionLocal
from models import Product, Request
from celery_app import celery_app


@celery_app.task
def process_images_task(request_id: str):
    db = SessionLocal()
    products = db.query(Product).filter(Product.request_id == request_id).all()

    for product in products:
        output_urls = []
        for input_url in product.input_urls.split(','):
            try:
                # Download the image
                response = requests.get(input_url)
                image = Image.open(BytesIO(response.content))

                # Compress the image by 50%
                output_image = BytesIO()
                image.save(output_image, format=image.format, quality=50)
                output_image.seek(0)

                # Save the compressed image (you can use S3 or any storage service)
                # For simplicity, we'll assume the function `upload_to_storage` uploads
                # the image and returns the URL.
                output_url = upload_to_storage(output_image)
                output_urls.append(output_url)
            except Exception as e:
                print(f"Failed to process image {input_url}: {e}")
                continue

        # Update the product with output URLs
        product.output_urls = ','.join(output_urls)
        db.add(product)
    db.commit()

    # Update the request status
    request = db.query(Request).filter(Request.id == request_id).first()
    request.status = "Completed"
    db.add(request)
    db.commit()
    db.close()
