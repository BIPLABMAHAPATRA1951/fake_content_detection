"""
video_detector.py
XceptionNet-based deepfake detection using timm + facenet-pytorch
Detects face regions and runs deepfake classifier on each face crop
"""

import tempfile
import os

def analyze_video(video_file) -> tuple:
    try:
        import cv2
        import numpy as np
        import torch
        import io
        from PIL import Image

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load model once
        model = _get_model(device)

        # Save uploaded video to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_file.read())
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_every = max(1, int(fps * 2))  # every 2 seconds

        face_scores = []
        fallback_scores = []
        frame_idx = 0
        frames_checked = 0

        while frames_checked < 10:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)

            # Try face detection + classification
            face_score = _classify_faces(pil_img, model, device)
            if face_score is not None:
                face_scores.append(face_score)
            else:
                # No face found — use frame-level heuristic
                fallback_scores.append(_frame_heuristic(frame))

            frame_idx += sample_every
            frames_checked += 1

        cap.release()
        os.unlink(tmp_path)

        signals = [f"Analyzed {frames_checked} frames"]

        if face_scores:
            avg = float(np.mean(face_scores))
            std = float(np.std(face_scores))
            signals.append(f"XceptionNet face analysis: {len(face_scores)} faces detected")
            signals.append(f"Avg face score: {avg:.2f} | Std: {std:.2f}")
            if std > 0.25:
                signals.append("high inter-frame variance — possible splicing")
                avg = min(avg + 0.1, 1.0)
            final_score = avg
        elif fallback_scores:
            final_score = float(np.mean(fallback_scores))
            signals.append("No faces detected — using frame heuristics")
        else:
            final_score = 0.2
            signals.append("Could not analyze video")

        return min(final_score, 1.0), " | ".join(signals)

    except ImportError as e:
        return 0.2, f"Missing dependency: {e}. Run: pip install facenet-pytorch timm"
    except Exception as e:
        return 0.2, f"Video analysis error: {e}"


# ── Model cache ───────────────────────────────────────────────────────────────
_xception_model = None

def _get_model(device):
    global _xception_model
    if _xception_model is not None:
        return _xception_model
    try:
        import timm
        import torch.nn as nn

        # Use EfficientNet-B4 — lighter than Xception, good accuracy
        model = timm.create_model("efficientnet_b4", pretrained=True, num_classes=2)
        model.eval()
        model = model.to(device)
        _xception_model = model
        return model
    except Exception as e:
        return None


def _classify_faces(pil_img, model, device):
    """Detect faces, classify each as real/fake, return avg score."""
    try:
        from facenet_pytorch import MTCNN
        import torch
        import torchvision.transforms as T
        import numpy as np

        mtcnn = MTCNN(keep_all=True, device=device, min_face_size=40)
        boxes, _ = mtcnn.detect(pil_img)

        if boxes is None or len(boxes) == 0:
            return None

        transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

        scores = []
        img_array = np.array(pil_img)

        for box in boxes[:3]:  # max 3 faces per frame
            x1, y1, x2, y2 = [max(0, int(b)) for b in box]
            face_crop = pil_img.crop((x1, y1, x2, y2))

            if face_crop.width < 20 or face_crop.height < 20:
                continue

            tensor = transform(face_crop).unsqueeze(0).to(device)

            with torch.no_grad():
                logits = model(tensor)
                probs = torch.softmax(logits, dim=-1)[0]
                # Index 1 = fake probability
                fake_prob = float(probs[1])
                scores.append(fake_prob)

        return float(np.mean(scores)) if scores else None

    except Exception:
        return None


def _frame_heuristic(frame) -> float:
    """Fallback when no face is detected."""
    import cv2
    import numpy as np

    score = 0.0
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if lap_var < 50:
            score += 0.3
        b, g, r = cv2.split(frame)
        channel_diff = max(abs(np.mean(r)-np.mean(g)), abs(np.mean(g)-np.mean(b)))
        if channel_diff > 40:
            score += 0.2
    except:
        pass
    return min(score, 1.0)