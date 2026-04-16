#history_utils.py
from typing import Any, Dict, List, Optional, Tuple

from models import Garment


def extract_garment_ids_from_history_entry(entry: Any) -> List[str]:
    """
    Acepta distintos formatos de historial:
    - ["id1", "id2", "id3"]
    - {"garment_ids": ["id1", "id2"]}
    - {"items": ["id1", "id2"]}
    - lista de Garment
    """
    if entry is None:
        return []

    if isinstance(entry, dict):
        if "garment_ids" in entry and isinstance(entry["garment_ids"], list):
            return [str(x) for x in entry["garment_ids"]]
        if "items" in entry and isinstance(entry["items"], list):
            return [str(x) for x in entry["items"]]
        return []

    if isinstance(entry, list):
        ids = []
        for item in entry:
            if isinstance(item, Garment):
                ids.append(str(item.id))
            else:
                ids.append(str(item))
        return ids

    return []


def build_recent_usage_maps(
    recent_outfits: Optional[List[Any]] = None,
) -> Tuple[Dict[str, int], Dict[Tuple[str, ...], int]]:
    """
    Devuelve:
    - garment_usage: cuántas veces aparece cada prenda en el historial reciente
    - combo_usage: cuántas veces aparece exactamente la misma combinación
    """
    garment_usage: Dict[str, int] = {}
    combo_usage: Dict[Tuple[str, ...], int] = {}

    if not recent_outfits:
        return garment_usage, combo_usage

    for entry in recent_outfits:
        garment_ids = extract_garment_ids_from_history_entry(entry)
        if not garment_ids:
            continue

        clean_ids = [str(gid) for gid in garment_ids]

        for gid in clean_ids:
            garment_usage[gid] = garment_usage.get(gid, 0) + 1

        combo_key = tuple(sorted(clean_ids))
        combo_usage[combo_key] = combo_usage.get(combo_key, 0) + 1

    return garment_usage, combo_usage


def repetition_penalty(
    items: List[Garment],
    recent_outfits: Optional[List[Any]] = None,
) -> int:
    """
    Penaliza repetir prendas y outfits recientes.
    Mantiene la penalización moderada para no romper el motor.
    """
    if not items or not recent_outfits:
        return 0

    garment_usage, combo_usage = build_recent_usage_maps(recent_outfits)
    penalty = 0

    current_ids = [str(g.id) for g in items]
    combo_key = tuple(sorted(current_ids))

    # 1) Penalización por repetir exactamente el mismo outfit
    exact_repeats = combo_usage.get(combo_key, 0)
    penalty += exact_repeats * 35

    # 2) Penalización por repetir prendas individuales
    for g in items:
        times_used = garment_usage.get(str(g.id), 0)

        if times_used == 0:
            continue

        base_per_repeat = {
            "top": 12,
            "bottom": 9,
            "shoes": 14,
            "outerwear": 14,
            "midlayer": 10,
            "accessory": 6,
        }.get(g.category, 8)

        penalty += times_used * base_per_repeat

    # 3) Penalización adicional si comparte demasiadas prendas con outfits recientes
    current_set = set(current_ids)

    for entry in recent_outfits:
        past_ids = set(extract_garment_ids_from_history_entry(entry))
        if not past_ids:
            continue

        shared = len(current_set.intersection(past_ids))

        if shared >= 3:
            penalty += 12
        elif shared == 2:
            penalty += 6

    return penalty