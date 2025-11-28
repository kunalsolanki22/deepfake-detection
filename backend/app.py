import sys
import os
import shutil
import tempfile
import torch
import uvicorn
import threading
import time
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# -------------------------------------------------------------------
# 1. FIX IMPORT PATH
# -------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from inference_utils import load_model, get_inference_transforms, predict_video
except ImportError as e:
    print(f"❌ Critical Error: {e}")
    sys.exit(1)

# -------------------------------------------------------------------
# 2. FASTAPI APP
# -------------------------------------------------------------------
app = FastAPI(title="DeepFake Sentinel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 3. MODEL SETUP (Lazy Loading)
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_xception_optuna.pth")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = None
transforms = None
is_loading = False  # Prevent duplicate loads

def load_all():
    """
    Safe lazy loading: loads the model only once.
    """
    global model, transforms, is_loading

    if model is not None:
        return

    if is_loading:
        # Another thread is already loading the model
        return

    print("🔥 Model loading started...")
    is_loading = True

    try:
        m = load_model(MODEL_PATH, device)
        t = get_inference_transforms()

        model = m
        transforms = t

        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error while loading model: {e}")
    finally:
        is_loading = False

# -------------------------------------------------------------------
# 4. BACKGROUND MODEL LOADING ON STARTUP (so port opens quickly)
# -------------------------------------------------------------------
@app.on_event("startup")
def load_model_background():
    """
    Runs in a background thread so Render's port scan succeeds.
    """
    def _load():
        time.sleep(1)  # Allow server to start first
        load_all()

    threading.Thread(target=_load, daemon=True).start()

# -------------------------------------------------------------------
# 5. ROUTES
# -------------------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "active",
        "model_loaded": model is not None,
        "device": str(device)
    }

@app.post("/predict_video/")
async def predict(file: UploadFile = File(...)):
    # Ensure model is loaded
    load_all()

    if model is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Model not loaded yet. Try again in a few seconds."}
        )

    # Save temp file
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Run inference
        result = predict_video(model, tmp_path, device, transforms)

        return {
            "filename": file.filename,
            "label": result["label"],
            "confidence": result["confidence"],
            "frames": result["frames"]
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Prediction error: {str(e)}"})

    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

# -------------------------------------------------------------------
# 6. LOCAL RUN
# -------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
