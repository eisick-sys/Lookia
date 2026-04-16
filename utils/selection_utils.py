#selection_utils.py
import random
from typing import List, Optional

from models import Garment


def filter_garments_by_category(
    wardrobe: List[Garment], category: str
) -> List[Garment]:
    return [g for g in wardrobe if g.category == category]


def filter_by_style(garments: List[Garment], style: str) -> List[Garment]:
    filtered = []

    for g in garments:
        secondary = g.secondary_styles or []
        if g.style == style or style in secondary:
            filtered.append(g)

    return filtered


def choose_item(items: List[Garment]) -> Optional[Garment]:
    if not items:
        return None
    return random.choice(items)