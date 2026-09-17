# Media Publisher — Setup & Run Guide 🚀

Complete guide to running the **Media Publisher** system with **FastAPI Backend**, **Cloudinary Storage**, **Vue 3 Frontend**, and **n8n Webhook Workflow**.

---

## 🏗️ Architecture Overview

```text
┌──────────────┐             multipart/form-data             ┌─────────────────┐
│              │ ──────────────────────────────────────────> │                 │
│              │ <────────────────────────────────────────── │                 │
│              │                 secure_url                  │                 │
│              │                                             │                 │
│  Vue 3 +     │                    JSON                     │ FastAPI Backend │
│  Vite UI     │ ──────────────────────────────────────────> │   (Port 8000)   │
│              │       { imageUrl, caption, platform }       │                 │
│              │                                             └────────┬────────┘
│              │                                                      │
└──────────────┘                                         upload image │ secure_url
                                                                      ▼
                                                             ┌─────────────────┐
                                                             │   Cloudinary    │
                                                             │     Storage     │
                                                             └─────────────────┘
                                                                      │
                                                       Forward JSON   │
                                                                      ▼
                                                             ┌─────────────────┐
                                                             │   n8n Webhook   │
                                                             │   (Port 5678)   │
                                                             └────────┬────────┘
                                                                      │
                                                          Switch Node │
                                                                      ▼
                                                             ┌─────────────────┐
                                                             │    Meta APIs    │
                                                             │ (IG & Facebook) │
                                                             └─────────────────┘
```

---

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+** & **npm**
- **n8n** running on `http://localhost:5678` (or your self-hosted instance)
- **Cloudinary account** (already configured in `backend/.env`)

---

## ⚙️ Step 1: Backend Setup & Run

### 1. Open a terminal in `backend/`:

```powershell
cd "c:\Users\balaj\Downloads\Do's\media-publisher\backend"
```

### 2. Activate the Virtual Environment:

```powershell
.\venv\Scripts\Activate.ps1
```

> *Note: If PowerShell scripts are restricted, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`*

### 3. Verify `.env` file:
Ensure `backend/.env` contains your Cloudinary credentials and n8n webhook:

```env
CLOUDINARY_CLOUD_NAME=cbl5jblk
CLOUDINARY_API_KEY=639289117314277
CLOUDINARY_API_SECRET=wSLqriwPClMS2MgSjbRSnGMD10I
N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/social-publisher
```

### 4. Start the FastAPI Server:

```powershell
python run.py
```
*Or using uvicorn directly:*
```powershell
uvicorn app.main:app --reload --port 8000
```

### 5. Verify the Backend:
- Root health check: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interactive API Docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💻 Step 2: Frontend Setup & Run

### 1. Open a second terminal in `frontend/`:

```powershell
cd "c:\Users\balaj\Downloads\Do's\media-publisher\frontend"
```

### 2. Install dependencies (if not already installed):

```powershell
npm install
```

### 3. Start the Vite Dev Server:

```powershell
npm run dev
```

The frontend will run at:
👉 **[http://localhost:5173/](http://localhost:5173/)**

*(Vite is configured to automatically proxy `/api` requests to `http://127.0.0.1:8000`)*

---

## 🧪 Step 3: End-to-End Testing

1. Open **[http://localhost:5173/](http://localhost:5173/)** in your browser.
2. **Upload an Image**:
   - Drag & drop an image or click the upload box to browse.
   - The file is uploaded immediately to Cloudinary.
   - The image preview, dimensions, format, and public URL appear on screen.
3. **Write a Caption**:
   - Fill in your post caption (e.g. `Our new product is live! 🚀 #launch`).
4. **Choose Platform**:
   - Select **Instagram**, **Facebook**, or **Both**.
5. **Click "Send Now 🚀"**:
   - The frontend sends the payload to `POST /api/social-posts/publish`.
   - FastAPI forwards the payload to your n8n webhook.
   - You will see a success confirmation banner with the n8n response details.
6. **Check n8n**:
   - Switch to your n8n workflow window and verify the execution completed successfully.

---

## 🛠️ API Endpoints Reference

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Health check | None |
| `POST` | `/api/uploads/image` | Upload image to Cloudinary | `multipart/form-data` with `file` |
| `POST` | `/api/social-posts/publish` | Forward post to n8n webhook | `{"imageUrl": "...", "caption": "...", "platform": "..."}` |

> **Note on Instagram Image URLs**: Meta's Instagram Graph API returns error `9004` if image URLs end with `.png`. The system automatically strips `.png` from the Cloudinary URL whenever publishing to **Instagram** or **Both**, allowing Instagram to download and accept the image without errors.

---

## 🔍 Troubleshooting

- **CORS Errors**: The FastAPI backend has CORS enabled with `allow_origins=["*"]`, and the Vite dev server also has a reverse proxy configured for `/api`.
- **n8n Connection Failed (502)**:
  - Check that n8n is running on `http://localhost:5678`.
  - In n8n, make sure you clicked **"Listen for test event"** if using `webhook-test/social-publisher`, or switch to the production `webhook/social-publisher` URL once the workflow is activated.
- **Port In Use**:
  - FastAPI default: `8000`
  - Vite default: `5173`
  - n8n default: `5678`

