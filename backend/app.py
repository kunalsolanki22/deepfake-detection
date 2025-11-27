import sys
import os
import shutil
import tempfile
import torch
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# --- 1. ROBUST IMPORT FIX ---
# This ensures we can find 'inference_utils.py' no matter where we run the script from
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from inference_utils import load_model, get_inference_transforms, predict_video
except ImportError as e:
    print(f"❌ Critical Error: {e}")
    print("Make sure you are in the 'backend' folder or running as a module.")
    sys.exit(1)

# --- 2. APP SETUP ---
app = FastAPI(title="DeepFake Sentinel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. MODEL LOADING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_xception_optuna.pth")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"🚀 Starting Server...")
print(f"📂 Model Path: {MODEL_PATH}")

try:
    model = load_model(MODEL_PATH, device)
    transforms = get_inference_transforms()
    if model:
        print("✅ Model Loaded Successfully!")
    else:
        print("⚠️ Model failed to load (Check path)")
except Exception as e:
    print(f"❌ Exception loading model: {e}")
    model = None

# --- 4. ROUTES ---
@app.get("/")
def home():
    return {"status": "active", "model_loaded": model is not None}

@app.post("/predict_video/")
async def predict(file: UploadFile = File(...)):
    if not model:
        return JSONResponse(status_code=503, content={"error": "Model not loaded on server."})
    
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)