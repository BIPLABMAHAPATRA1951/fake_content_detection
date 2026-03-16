WEIGHTS = {
    "text":  0.25,
    "image": 0.35,
    "audio": 0.20,
    "video": 0.20,
}

def compute_verdict(scores: dict) -> tuple:
    if not scores:
        return "UNCERTAIN", 0.5
    total_weight = sum(WEIGHTS.get(m, 0.25) for m in scores)
    weighted_sum = sum(scores[m] * WEIGHTS.get(m, 0.25) for m in scores)
    final_score = weighted_sum / total_weight
    if final_score >= 0.80:
        verdict = "MANIPULATED"
    elif final_score <= 0.30:
        verdict = "AUTHENTIC"
    else:
        verdict = "UNCERTAIN"
    return verdict, final_score
