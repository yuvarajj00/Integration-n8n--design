from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from app.services.cloudinary_service import upload_image
from app.config import N8N_WEBHOOK_URL

app = FastAPI(title="Media Publisher API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PublishPostRequest(BaseModel):
    imageUrl: str
    caption: str
    platform: str  # instagram, facebook, both

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Media Publisher API is running"}

@app.post("/api/uploads/image")
async def upload_post_image(file: UploadFile = File(...)):
    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="File type is missing"
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    try:
        result = upload_image(file.file)
        return {
            "success": True,
            "image": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )

@app.post("/api/social-posts/publish")
async def publish_social_post(request: PublishPostRequest):
    if not request.imageUrl:
        raise HTTPException(status_code=400, detail="Image URL is required")
    if not request.caption:
        raise HTTPException(status_code=400, detail="Caption is required")
    if request.platform not in ["instagram", "facebook", "both"]:
        raise HTTPException(status_code=400, detail="Platform must be 'instagram', 'facebook', or 'both'")

    import re

    image_url = request.imageUrl
    platform = request.platform.lower()

    # Meta Instagram Graph API strictly requires JPEG format (image/jpeg).
    # It rejects PNG completely ("Only photo or video can be accepted as media type").
    # If the URL ends with .png, replace with .jpg so Cloudinary automatically delivers JPEG.
    # If the URL has no extension, append .jpg.
    if platform in ["instagram", "both"] and image_url:
        if re.search(r'\.png(?=[\?#]|$)', image_url, flags=re.IGNORECASE):
            image_url = re.sub(r'\.png(?=[\?#]|$)', '.jpg', image_url, flags=re.IGNORECASE)
        elif not re.search(r'\.(jpe?g|png|webp)(?=[\?#]|$)', image_url, flags=re.IGNORECASE):
            image_url = re.sub(r'(?=[?#]|$)', '.jpg', image_url, count=1)

    payload = {
        "imageUrl": image_url,
        "image_url": image_url,
        "caption": request.caption,
        "platform": platform,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(N8N_WEBHOOK_URL, json=payload)
            response_data = None
            try:
                response_data = response.json()
            except Exception:
                response_data = {"raw": response.text}

            return {
                "success": response.is_success,
                "status_code": response.status_code,
                "message": "Post forwarded to n8n webhook successfully" if response.is_success else "n8n webhook returned error",
                "n8n_response": response_data
            }
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach n8n webhook ({N8N_WEBHOOK_URL}). Ensure n8n is running and listening: {str(exc)}"
        )
