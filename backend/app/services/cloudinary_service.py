import cloudinary
import cloudinary.uploader
from app.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

def upload_image(file):
    result = cloudinary.uploader.upload(
        file,
        folder="brandrelay/posts",
        resource_type="image",
        format="jpg",
    )
    return {
        "public_id": result.get("public_id"),
        "url": result.get("secure_url"),
        "width": result.get("width"),
        "height": result.get("height"),
        "format": result.get("format"),
    }

