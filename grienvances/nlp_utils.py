# Very simple sentiment & priority heuristic without external packages
# You can replace this with TextBlob/VADER later.
NEGATIVE_WORDS = {'not','no','angry','bad','poor','worst','urgent','immediately','delay','issue','problem','broken','fail','harass'}
POSITIVE_WORDS = {'good','great','thanks','resolved','appreciate','happy'}

def simple_sentiment(text: str) -> float:
    text = (text or '').lower()
    score = 0
    for w in NEGATIVE_WORDS:
        if w in text: score -= 1
    for w in POSITIVE_WORDS:
        if w in text: score += 1
    # normalize rough score to -1..1
    if score == 0: return 0.0
    return max(-1.0, min(1.0, score/5.0))

def priority_from_sentiment(score: float) -> str:
    if score <= -0.6:
        return 'High'
    if score <= -0.2:
        return 'Normal'  # medium negative
    return 'Normal'