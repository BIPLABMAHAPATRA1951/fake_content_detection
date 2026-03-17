<div align="center">

# 🛡️ DeepGuard
### Multimodal AI-Powered Deepfake Detection System

🔗 **Live Demo:** [DeepGuard — AI Detection System · Streamlit](https://fakecontentdetection-6fqbrmugshbaxkxjxcymqd.streamlit.app)

> An intelligent system capable of detecting AI-generated and manipulated content across **text, images, audio, and video** using state-of-the-art machine learning models.

</div>

---

## 🎯 Problem Statement

The rapid growth of generative AI has enabled the creation of highly realistic deepfake videos, manipulated images, and AI-generated text that can spread misinformation and deceive users. Such content poses serious risks to public trust, media credibility, and digital security.

**DeepGuard** addresses this challenge by providing a unified multimodal detection system that analyzes content across all media types simultaneously.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Text Detection** | RoBERTa transformer model trained on GPT-2/ChatGPT outputs |
| 🖼️ **Image Detection** | EXIF metadata analysis + Gemini Vision AI |
| 🎙️ **Audio Detection** | Spectral analysis — flatness, MFCC, pitch consistency |
| 🎬 **Video Detection** | Frame-level EfficientNet + MTCNN face detection |
| ⚡ **Full Multimodal Scan** | Cross-modal consistency check with fusion engine |
| 📊 **Dashboard** | Real-time analytics with 3D charts |
| 📋 **Scan History** | Track and filter all previous detections |
| 🔐 **Auth System** | Login, Register, Admin panel with user management |
| 🌙 **Glassmorphism UI** | Modern dark theme with blur effects |

---

## 🏗️ Architecture

```
User Input (Text / Image / Audio / Video)
              ↓
┌─────────────────────────────────────┐
│         Detection Modules           │
│  📝 Text  🖼️ Image  🎙️ Audio  🎬 Video │
└─────────────────────────────────────┘
              ↓
    Confidence Scores (per modality)
              ↓
       🔀 Fusion Engine
    (Weighted Average + Cross-modal)
              ↓
   ✅ AUTHENTIC / 🚨 MANIPULATED / ⚠️ UNCERTAIN
```

---

## 🔬 Detection Methods

### 📝 Text Detection
- **Model:** `roberta-base-openai-detector` (HuggingFace)
- Detects statistical patterns unique to AI-generated text
- Heuristic fallback: AI phrase detection, sentence uniformity, lexical diversity

### 🖼️ Image Detection
- **EXIF Metadata Analysis** — Real camera photos contain rich metadata; AI images don't
- **Gemini Vision** — Google's multimodal AI analyzes visual artifacts
- Detects: unnatural skin, distorted hands, impossible lighting, garbled text

### 🎙️ Audio Detection
- **Library:** `librosa`
- Spectral flatness analysis (TTS audio is unnaturally flat)
- MFCC variance measurement (monotone timbre = synthetic)
- Pitch consistency detection (robotic prosody)
- RMS energy uniformity check

### 🎬 Video Detection
- **Face Detection:** MTCNN (facenet-pytorch)
- **Classification:** EfficientNet-B4 (timm)
- Frame sampling every 2 seconds
- Inter-frame consistency analysis

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.12+
CUDA-capable GPU (recommended)
```

### Installation
```bash
# Clone the repository
git clone https://github.com/BIPLABMAHAPATRA1951/fake_content_detection.git
cd fake_content_detection

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Default Login
```
Username: admin
Password: admin@123
```

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technology |
|---|---|
| **Frontend** | Streamlit, Plotly |
| **ML/AI** | PyTorch, HuggingFace Transformers |
| **Computer Vision** | OpenCV, facenet-pytorch, timm |
| **Audio Processing** | librosa, soundfile |
| **Vision AI** | Google Gemini API |
| **Database** | SQLite |
| **Language** | Python 3.12 |

</div>

---

## 📊 Model Performance

| Modality | Model | Accuracy |
|---|---|---|
| Text | RoBERTa-base | ~70-85% on GPT-2 text |
| Image | EXIF + Gemini | High on AI-generated faces |
| Audio | Spectral Analysis | ~80% on TTS (gTTS) |
| Video | EfficientNet-B4 | Beta — frame-level detection |

> **Note:** Text detection accuracy varies based on the AI model used to generate the content. State-of-the-art models like GPT-4 and Claude are harder to detect — this is an open research problem even for leading AI labs.

---

## 📁 Project Structure

```
fake_content_detection/
├── app.py                    # Main Streamlit application
├── auth.py                   # Authentication system (SQLite)
├── fusion.py                 # Score fusion engine
├── requirements.txt          # Python dependencies
├── packages.txt              # System dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── detectors/
    ├── __init__.py
    ├── text_detector.py      # RoBERTa text detection
    ├── image_detector.py     # EXIF + Gemini image detection
    ├── audio_detector.py     # Spectral audio detection
    └── video_detector.py     # Frame-based video detection
```

---

## 🔮 Future Roadmap

- [ ] Fine-tune XceptionNet on FaceForensics++ dataset
- [ ] Add support for real-time webcam deepfake detection
- [ ] Implement blockchain-based content verification
- [ ] Browser extension for instant web content verification
- [ ] API endpoint for third-party integration
- [ ] Multi-language text detection support

---

## ⚠️ Limitations

- **Text Detection:** Struggles with humanized AI content and non-English text
- **Video Detection:** Not optimized for Sora/state-of-the-art generative video
- **Audio Detection:** ElevenLabs-quality TTS may evade detection
- Video deepfake detection requires FaceForensics++ fine-tuned models for production use

---

## 👨‍💻 Author

**Biplab Mahapatra**

[![GitHub](https://img.shields.io/badge/GitHub-BIPLABMAHAPATRA1951-black?logo=github)](https://github.com/BIPLABMAHAPATRA1951)

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
Built with ❤️ for Hackathon 2026
</div>
