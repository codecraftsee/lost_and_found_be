from app.claims.models import Claim
from app.items.models import Item


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().lower()


def _fuzzy_match(answer: str | None, expected: str | None) -> bool:
    """Simple fuzzy comparison: case-insensitive, trimmed, substring check."""
    a = _normalize(answer)
    e = _normalize(expected)
    if not a or not e:
        return False
    return a == e or a in e or e in a


def verify_claim_answers(claim: Claim, item: Item) -> tuple[bool, float]:
    """
    Compare claim answers against item's private fields.
    Returns (is_verified, match_percentage).
    """
    checks: list[bool] = []

    if item.private_brand:
        checks.append(_fuzzy_match(claim.answer_brand, item.private_brand))
    if item.private_color:
        checks.append(_fuzzy_match(claim.answer_color, item.private_color))
    if item.private_markings:
        checks.append(_fuzzy_match(claim.answer_markings, item.private_markings))
    if item.private_contents:
        checks.append(_fuzzy_match(claim.answer_contents, item.private_contents))
    if item.private_exact_location:
        checks.append(_fuzzy_match(claim.answer_exact_location, item.private_exact_location))

    if not checks:
        return False, 0.0

    correct = sum(checks)
    match_pct = correct / len(checks)

    # Require at least 60% match to pass verification
    return match_pct >= 0.6, match_pct
