import spacy

# Load once at import time
_nlp = spacy.load("en_core_web_sm")

PROMISE_TRIGGERS = [
    "will", "plan", "promise", "deliver", "expand", "create",
    "freeze", "build", "fund", "ban", "provide", "make"
]

def extract_promises(text: str) -> list[dict]:
    """
    v1 heuristic:
    - split into sentences
    - keep sentences that contain a trigger word suggesting a commitment/action
    """
    doc = _nlp(text)
    promises: list[dict] = []

    for sent in doc.sents:
        s = sent.text.strip()
        s_lower = s.lower()

        if len(s) < 25:
            continue

        if any(t in s_lower for t in PROMISE_TRIGGERS):
            promises.append({
                "policy_area": guess_policy_area(s_lower),
                "promise": s
            })

    return promises

def guess_policy_area(sentence_lower: str) -> str:
    if any(k in sentence_lower for k in ["rent", "housing", "tenant", "stabil"]):
        return "housing"
    if any(k in sentence_lower for k in ["bus", "subway", "transit", "fare"]):
        return "transit"
    if any(k in sentence_lower for k in ["grocery", "food", "market"]):
        return "affordability"
    if any(k in sentence_lower for k in ["childcare", "daycare", "kids"]):
        return "childcare"
    return "other"
