"""Placeholder violation logic (ROI + temporal rules to be added)."""


def infer_violation_from_labels(labels: list[str]) -> bool:
    """
    Simple demo heuristic: hand visible without scooper in the same frame.
    Replace with ROI FSM per task spec.
    """
    lower = [x.lower() for x in labels]
    has_hand = any("hand" in s for s in lower)
    has_scooper = any("scoop" in s for s in lower)
    return bool(has_hand and not has_scooper)
