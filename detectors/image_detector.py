"""
image_detector.py
1. EXIF metadata analysis
2. Gemini Vision (google-genai, new SDK)
"""

import io
import re

def analyze_image(image_file, api_key: str = None, gemini_key: str = None) -> tuple:
    scores = []
    explanations = []

    image_file.seek(0)
    meta_score, meta_reason = _check_metadata(image_file)
    scores.append(meta_score)
    explanations.append(f"Metadata: {meta_reason}")

    g_key = gemini_key or api_key
    if g_key:
        image_file.seek(0)
        vis_score, vis_reason = _gemini_vision(image_file, g_key)
        if vis_score is not None:
            scores.append(vis_score)
            explanations.append(f"Gemini Vision: {vis_reason}")

    final = sum(scores) / len(scores)
    return final, " | ".join(explanations)


def _check_metadata(image_file) -> tuple:
    try:
        from PIL import Image
        img = Image.open(image_file)
        exif_data = img._getexif() if hasattr(img, "_getexif") else None
        if exif_data:
            important_tags = {271, 272, 306, 36867, 34853}
            found = important_tags & set(exif_data.keys())
            if len(found) >= 2:
                return 0.1, f"Rich EXIF found ({len(found)} camera tags) — likely real"
            return 0.5, "Minimal EXIF — possibly AI-generated"
        else:
            return 0.65, "No EXIF metadata — common in AI-generated images"
    except Exception as e:
        return 0.5, f"Metadata error: {e}"


def _gemini_vision(image_file, api_key: str) -> tuple:
    try:
        from google import genai
        from google.genai import types
        from PIL import Image

        client = genai.Client(api_key=api_key)
        img = Image.open(image_file)

        prompt = """You are a highly specialized AI image forensics expert with 10 years of experience detecting synthetic and AI-generated content.

Your task: Determine if this image was created by an AI (Midjourney, DALL-E, Stable Diffusion, GAN, deepfake, etc.) or is a genuine real photograph taken by a camera.

IMPORTANT RULES:
- If the image looks like a real photograph taken by a real camera, give score 0.0 to 0.2
- Only increase score if you find CLEAR and DEFINITE AI artifacts
- Do NOT penalize real photos for being high quality or well-lit
- Real photos have natural imperfections — embrace them

AI-GENERATED ARTIFACTS to look for (only flag if clearly present):
1. Skin that looks like plastic, wax, or overly airbrushed
2. Extra, missing, or fused fingers and hands
3. Eyes that are glassy, asymmetric, or have impossible reflections  
4. Hair that clumps unnaturally, floats, or merges with background
5. Background objects that are warped, melted, or physically impossible
6. Text that is garbled, morphed, nonsensical, or illegible
7. Lighting that comes from multiple impossible directions simultaneously
8. Clothing or fabric with impossible or repeating patterns
9. Ears, teeth, or facial features that are asymmetric in an unnatural way
10. Overall "uncanny valley" feeling — looks almost real but slightly off

SCORING GUIDE:
0.0 - 0.2 : Clearly a real photograph, no AI artifacts
0.2 - 0.4 : Mostly real, minor post-processing possible
0.4 - 0.6 : Uncertain — some suspicious elements but not conclusive
0.6 - 0.8 : Likely AI-generated — multiple clear artifacts found
0.8 - 1.0 : Definitely AI-generated — obvious synthetic artifacts

Respond ONLY in this exact format, nothing else:
SCORE: <float>
REASON: <one clear sentence explaining the most important evidence>"""

        response = client.models.generate_content(
            model="gemini-1.5-flash-8b",
            contents=[prompt, img]
        )

        raw = response.text.strip()
        score_match = re.search(r"SCORE:\s*([\d.]+)", raw)
        reason_match = re.search(r"REASON:\s*(.+)", raw)

        score = float(score_match.group(1)) if score_match else 0.5
        reason = reason_match.group(1) if reason_match else raw[:120]

        return min(max(score, 0.0), 1.0), reason

    except Exception as e:
        return None, f"Gemini error: {e}"