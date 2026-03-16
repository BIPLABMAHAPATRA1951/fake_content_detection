import re

_tokenizer = None
_model = None

def _load_model():
    global _tokenizer, _model
    if _model is not None:
        return True
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        model_name = "roberta-base-openai-detector"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSequenceClassification.from_pretrained(
            model_name, ignore_mismatched_sizes=True
        )
        _model.eval()
        return True
    except Exception as e:
        print(f"Model load failed: {e}")
        return False

def analyze_text(text: str, api_key: str = None) -> tuple:
    if not text.strip():
        return 0.0, "No text provided"
    score, explanation = _roberta_classify(text)
    if score is not None:
        return score, explanation
    return _heuristic_classify(text)

def _roberta_classify(text: str):
    try:
        import torch
        if not _load_model():
            return None, "Model could not be loaded"
        inputs = _tokenizer(
            text[:512],
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        with torch.no_grad():
            outputs = _model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]
        fake_prob = float(probs[1])
        if fake_prob > 0.75:
            label = "Very likely AI-generated"
        elif fake_prob > 0.55:
            label = "Possibly AI-generated"
        elif fake_prob > 0.4:
            label = "Uncertain — borderline"
        else:
            label = "Likely human-written"
        return fake_prob, f"RoBERTa detector: {label} (confidence: {fake_prob:.0%})"
    except Exception as e:
        return None, f"Model error: {e}"

def _heuristic_classify(text: str):
    signals = []
    score = 0.0
    words = text.split()
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
    if len(sentences) > 3:
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        if variance < 8:
            score += 0.2
            signals.append("uniform sentence lengths")
    first_person = len(re.findall(r"\b(I|me|my|mine|myself)\b", text, re.I))
    if first_person == 0 and len(words) > 60:
        score += 0.15
        signals.append("no first-person pronouns")
    ai_phrases = [
        "it is worth noting", "it is important to note", "in conclusion",
        "to summarize", "as an ai", "delve into", "it's crucial to",
        "in today's world", "in the realm of", "furthermore", "moreover",
    ]
    found = [p for p in ai_phrases if p.lower() in text.lower()]
    score += min(len(found) * 0.1, 0.35)
    if found:
        signals.append(f"AI phrases: {', '.join(found[:3])}")
    if not signals:
        reason = "No strong AI signals (heuristic mode)"
    else:
        reason = "Heuristic signals: " + " | ".join(signals)
    return min(score, 1.0), reason
