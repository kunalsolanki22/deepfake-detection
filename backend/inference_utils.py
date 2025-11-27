import torch
import timm
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import mediapipe as mp
import base64

# ===========================
# 1. Model Architecture
# ===========================
def build_model(num_classes=2):
    model = timm.create_model('xception', pretrained=False)
    in_features = model.fc.in_features
    model.fc = torch.nn.Sequential(
        torch.nn.Linear(in_features, 512),
        torch.nn.ReLU(),
        torch.nn.Dropout(0.5),
        torch.nn.Linear(512, num_classes)
    )
    return model

def load_model(model_path, device):
    try:
        model = build_model()
        checkpoint = torch.load(model_path, map_location=device)
        model.load_state_dict(checkpoint)
        model.to(device)
        model.eval()
        print(f"✅ Model loaded: {model_path}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

# ===========================
# 2. Preprocessing
# ===========================
def get_inference_transforms():
    return A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2()
    ])

# ===========================
# 3. Face Extraction (With BBox)
# ===========================
mp_face_detection = mp.solutions.face_detection.FaceDetection(
    model_selection=1, min_detection_confidence=0.5
)

def extract_faces_with_bbox(frame_bgr):
    """
    Returns list of tuples: (face_crop, (x, y, w, h))
    """
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    results = mp_face_detection.process(frame_rgb)
    faces_data = []
    
    if results.detections:
        h, w, _ = frame_bgr.shape
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)
            
            # Boundary checks
            x, y = max(0, x), max(0, y)
            
            # Ensure detection is within frame
            if x + bw > w: bw = w - x
            if y + bh > h: bh = h - y

            face = frame_rgb[y:y+bh, x:x+bw]
            if face.size > 0 and bw > 20 and bh > 20: # Ignore tiny artifacts
                faces_data.append((face, (x, y, bw, bh)))
    return faces_data

def encode_frame_to_base64(frame):
    """Encodes an OpenCV image to a Base64 string for JSON transfer."""
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    return base64.b64encode(buffer).decode('utf-8')

# ===========================
# 4. Prediction Logic (With Visuals)
# ===========================
def predict_video(model, video_path, device, transform):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"label": "Error", "confidence": 0.0, "frames": []}

    predictions = []
    analyzed_frames = [] # Stores base64 strings of annotated frames
    frame_count = 0
    
    # Smart Skip Strategy: Process frequently but only save a few frames
    frames_to_save = 4 
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame_count += 1
        
        # Analyze every 10th frame (balance speed vs accuracy)
        if frame_count % 10 != 0: continue 
        
        faces_data = extract_faces_with_bbox(frame)
        frame_has_detection = False
        
        # Working copy for drawing (so we don't mess up the raw frame for prediction)
        vis_frame = frame.copy()
        
        for face, (x, y, w, h) in faces_data:
            try:
                # Preprocess & Predict
                processed = transform(image=face)["image"].unsqueeze(0).to(device)
                with torch.no_grad():
                    output = model(processed)
                    probs = torch.softmax(output, dim=1)
                    fake_prob = probs[0, 1].item()
                    predictions.append(fake_prob)
                    
                    # --- Visualization ---
                    # Red for Fake (>50%), Green for Real
                    color = (0, 0, 255) if fake_prob > 0.5 else (0, 255, 0)
                    label = f"FAKE: {fake_prob*100:.1f}%" if fake_prob > 0.5 else f"REAL: {(1-fake_prob)*100:.1f}%"
                    
                    # Draw BBox
                    cv2.rectangle(vis_frame, (x, y), (x+w, y+h), color, 3)
                    
                    # Draw Label Background for readability
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(vis_frame, (x, y - 30), (x + text_size[0], y), color, -1)
                    
                    # Draw Text
                    cv2.putText(vis_frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    frame_has_detection = True
            except Exception as e:
                continue
        
        # Save frame IF it has a detection AND we haven't hit our limit
        if frame_has_detection and len(analyzed_frames) < frames_to_save:
            # Resize to reduce JSON payload size (HD is too big)
            h, w = vis_frame.shape[:2]
            scale = 640 / w
            resized = cv2.resize(vis_frame, (640, int(h * scale)))
            analyzed_frames.append(encode_frame_to_base64(resized))
            
    cap.release()
    
    if not predictions: 
        return {"label": "No Faces", "confidence": 0.0, "frames": []}
    
    # 70th Percentile Aggregation
    score = np.percentile(predictions, 70)
    
    return {
        "label": "Fake" if score > 0.5 else "Real", 
        "confidence": float(score),
        "frames": analyzed_frames
    }