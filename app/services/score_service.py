def score_feasibility(promise: str, policy_area: str) -> tuple[float, str]:
    """
    v1 heuristic feasibility scoring.
    Returns:
      (score in [0,1], notes string)

    This is intentionally simple so your end-to-end pipeline works.
    You will replace this with real scoring later (authority + budget + ops).
    """
    p = (promise or "").lower()
    area = (policy_area or "").lower()

    score = 0.50
    notes = []

    # Heuristic adjustments
    if any(w in p for w in ["state law", "federal", "congress", "albany"]):
        score -= 0.20
        notes.append("Likely requires state/federal coordination.")

    if any(w in p for w in ["pilot", "phase", "study"]):
        score += 0.10
        notes.append("Pilot/phased approach improves implementability.")

    if any(w in p for w in ["free", "universal", "for all"]):
        score -= 0.10
        notes.append("Universal/free scope suggests higher funding needs.")

    # Area nudges (placeholder)
    if area == "housing":
        score += 0.05
    elif area == "transit":
        score -= 0.05

    # Clamp
    score = max(0.0, min(1.0, score))
    note_str = " ".join(notes) if notes else "Heuristic v1 score (replace with data-driven model)."
    return score, note_str
