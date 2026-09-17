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
            urls_to_try = [N8N_WEBHOOK_URL]
            if "/webhook/" in N8N_WEBHOOK_URL:
                urls_to_try.append(N8N_WEBHOOK_URL.replace("/webhook/", "/webhook-test/"))
            elif "/webhook-test/" in N8N_WEBHOOK_URL:
                urls_to_try.append(N8N_WEBHOOK_URL.replace("/webhook-test/", "/webhook/"))

            last_response = None
            response_data = None
            for url in urls_to_try:
                try:
                    response = await client.post(url, json=payload)
                    last_response = response
                    try:
                        response_data = response.json()
                    except Exception:
                        response_data = {"raw": response.text}

                    if response.is_success:
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "webhook_url": url,
                            "message": "Post forwarded to n8n webhook successfully",
                            "n8n_response": response_data,
                        }
                except httpx.RequestError:
                    continue

            error_msg = response_data.get("message") if isinstance(response_data, dict) else str(response_data)
            status = last_response.status_code if last_response else 502
            raise HTTPException(
                status_code=status,
                detail=f"n8n webhook returned error (HTTP {status}): {error_msg or 'Check n8n execution log'}"
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach n8n webhook: {str(exc)}"
        )
