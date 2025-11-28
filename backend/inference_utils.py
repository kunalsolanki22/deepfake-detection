import torch
import timm
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import mediapipe as mp
import base64
import time
# ===========================
# 1. MODEL ARCHITECTURE
# ===========================
def build_model(num_classes=2):
    model = timm.create_model('legacy_xception', pretrained=False)
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
# 2. PREPROCESSING
# ===========================
def get_inference_transforms():
    return A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2()
    ])


# ===========================
# 3. FASTER + SAFER MEDIAPIPE
# ===========================

mp_face_detection = mp.solutions.face_detection.FaceDetection(
    model_selection=0,          # ✔ fastest model (works best on low CPU servers)
    min_detection_confidence=0.4
)


def extract_faces_with_bbox(frame_bgr):
    """
    Returns a list of: (face_crop, (x, y, w, h))
    Robust version for Render deployment.
    """

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    results = mp_face_detection.process(frame_rgb)
    faces_data = []

    if not results.detections:
        return faces_data

    h, w, _ = frame_bgr.shape

    for detection in results.detections:
        bbox = detection.location_data.relative_bounding_box

        # Safe bounding box conversion
        x1 = max(0, int(bbox.xmin * w))
        y1 = max(0, int(bbox.ymin * h))
        bw = int(bbox.width * w)
        bh = int(bbox.height * h)

        x2 = min(w, x1 + bw)
        y2 = min(h, y1 + bh)

        face = frame_rgb[y1:y2, x1:x2]

        # Reject tiny noise boxes
        if face.size == 0 or (x2-x1) < 30 or (y2-y1) < 30:
            continue

        faces_data.append((face, (x1, y1, x2-x1, y2-y1)))

    return faces_data


def encode_frame_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    return base64.b64encode(buffer).decode('utf-8')


# ===========================
# 4. MAIN VIDEO INFERENCE
# ===========================

def predict_video(model, video_path, device, transform):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"label": "Error", "confidence": 0.0, "frames": []}

    predictions = []
    analyzed_frames = []
    frame_count = 0

    MAX_FRAMES = 80               # Hard limit → prevents Render freeze
    SAVE_LIMIT = 4                # Max frames saved for UI
    START_TIME = time.time()
    TIME_LIMIT = 15               # 15 seconds max inference time

    while True:
        # ---------- TIMEOUT ----------
        if time.time() - START_TIME > TIME_LIMIT:
            print("⛔ TIMEOUT: Returning partial results")
            break

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # ---------- Stop after MAX_FRAMES ----------
        if frame_count > MAX_FRAMES:
            print("⚠️ MAX FRAME LIMIT REACHED")
            break

        # Process first 30 frames, then sample every 5th
        if frame_count > 30 and (frame_count % 5 != 0):
            continue

        faces_data = extract_faces_with_bbox(frame)
        vis_frame = frame.copy()

        if len(faces_data) == 0:
            continue

        for face, (x, y, w, h) in faces_data:
            try:
                processed = transform(image=face)["image"].unsqueeze(0).to(device)

                with torch.no_grad():
                    output = model(processed)
                    probs = torch.softmax(output, dim=1)
                    fake_prob = probs[0, 1].item()
                    predictions.append(fake_prob)

                color = (0, 0, 255) if fake_prob > 0.5 else (0, 255, 0)
                label = f"{'FAKE' if fake_prob>0.5 else 'REAL'} {fake_prob*100:.1f}%"

                cv2.rectangle(vis_frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(vis_frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

            except:
                continue

        if len(analyzed_frames) < SAVE_LIMIT:
            h, w = vis_frame.shape[:2]
            resized = cv2.resize(vis_frame, (480, int(h * (480 / w))))
            analyzed_frames.append(encode_frame_to_base64(resized))

    cap.release()

    if len(predictions) == 0:
        return {"label": "No Faces", "confidence": 0.0, "frames": []}

    score = float(np.percentile(predictions, 70))

    return {
        "label": "Fake" if score > 0.5 else "Real",
        "confidence": score,
        "frames": analyzed_frames
    }
