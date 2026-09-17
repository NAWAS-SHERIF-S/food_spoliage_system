"""Shelf-life estimation and preservation advice service."""

from __future__ import annotations

from dataclasses import dataclass

from freshness.constants import PRESERVATION_TIPS, PRODUCE_BASE_SHELF_LIFE


@dataclass(slots=True)
class ShelfLifeEstimate:
    produce_type: str
    freshness_state: str
    confidence: float
    days_min: int
    days_max: int
    recommended_days: int
    preservation_tip: str
    status_badge: str  # "Fresh (x-y days left)", "Use Soon (1-2 days left)", "Rotten / Expired"


def get_preservation_tip(produce_type: str) -> str:
    """Return tailored preservation tip for a produce type."""
    return PRESERVATION_TIPS.get(
        produce_type.lower(),
        PRESERVATION_TIPS["unknown"],
    )


def estimate_shelf_life(
    produce_type: str,
    freshness_state: str,
    confidence: float = 1.0,
) -> ShelfLifeEstimate:
    """Calculate remaining shelf-life days and status badge from prediction."""
    ptype = produce_type.lower()
    fstate = freshness_state.lower()
    tip = get_preservation_tip(ptype)

    if fstate == "rotten" or ptype == "unknown" or fstate == "n_a":
        return ShelfLifeEstimate(
            produce_type=ptype,
            freshness_state=fstate,
            confidence=confidence,
            days_min=0,
            days_max=0,
            recommended_days=0,
            preservation_tip=tip if fstate != "rotten" else "Item is spoiled. Dispose safely or compost.",
            status_badge="Spoiled / Expired",
        )

    # Fresh produce item
    base_min, base_max = PRODUCE_BASE_SHELF_LIFE.get(ptype, (3, 7))
    
    # Adjust recommended days based on confidence
    range_span = base_max - base_min
    rec_days = int(round(base_min + (range_span * max(0.5, confidence))))
    rec_days = max(1, min(base_max, rec_days))

    if rec_days <= 2:
        badge = f"Use Soon ({rec_days} day{'s' if rec_days > 1 else ''} left)"
    else:
        badge = f"Fresh ({base_min}–{base_max} days left)"

    return ShelfLifeEstimate(
        produce_type=ptype,
        freshness_state=fstate,
        confidence=confidence,
        days_min=base_min,
        days_max=base_max,
        recommended_days=rec_days,
        preservation_tip=tip,
        status_badge=badge,
    )
