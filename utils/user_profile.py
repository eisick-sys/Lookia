#user_profile.py
from typing import Dict, List, Optional

from models import Garment, OutfitFeedback
from utils.garment_utils import all_styles

# =========================================================
# PERFIL AUTOMÁTICO DEL USUARIO
# =========================================================

def build_user_style_profile(
    feedback_list: List[OutfitFeedback],
    wardrobe: List[Garment],
) -> Dict[str, Dict[str, int]]:
    """
    Construye un perfil simple del usuario a partir del feedback.
    Aprende preferencias por:
    - estilo
    - color
    - nivel de formalidad
    """

    if not feedback_list or not wardrobe:
        return {
            "style": {},
            "color": {},
            "dress": {},
        }

    garment_map = {g.id: g for g in wardrobe}

    style_pref: Dict[str, int] = {}
    color_pref: Dict[str, int] = {}
    dress_pref: Dict[str, int] = {}

    for fb in feedback_list:
        delta = 1 if fb.liked else -1

        for garment_id in fb.garment_ids:
            garment = garment_map.get(garment_id)
            if not garment:
                continue

            for style in all_styles(garment):
                style_pref[style] = style_pref.get(style, 0) + delta

            color_pref[garment.color] = color_pref.get(garment.color, 0) + delta
            dress_pref[garment.dress_level] = (
                dress_pref.get(garment.dress_level, 0) + delta
            )

    return {
        "style": style_pref,
        "color": color_pref,
        "dress": dress_pref,
    }


def user_style_bonus(
    garment: Garment,
    user_profile: Optional[Dict[str, Dict[str, int]]] = None,
) -> int:
    """
    Bonus por afinidad histórica del usuario.
    Se mantiene moderado para ayudar, pero sin dominar todo el motor.
    """

    if not user_profile:
        return 0

    bonus = 0

    style_pref = user_profile.get("style", {})
    color_pref = user_profile.get("color", {})
    dress_pref = user_profile.get("dress", {})

    for style in all_styles(garment):
        bonus += style_pref.get(style, 0) * 2

    bonus += color_pref.get(garment.color, 0)
    bonus += dress_pref.get(garment.dress_level, 0)

    return max(-12, min(12, bonus))


def calculate_feedback_bonus(
    items: List[Garment],
    feedback_list: List[OutfitFeedback],
    occasion: str,
    mood: str,
    activity: str,
    weather_tag: str,
) -> int:
    if not feedback_list:
        return 0

    bonus = 0
    current_ids = {g.id for g in items}

    for fb in feedback_list:
        fb_ids = set(fb.garment_ids)
        shared_ids = len(current_ids.intersection(fb_ids))

        if shared_ids == 0:
            continue

        score = 0

        if current_ids == fb_ids:
            score += 30
        else:
            score += shared_ids * 6

        if fb.occasion == occasion:
            score += 5
        if fb.mood == mood:
            score += 4
        if fb.activity == activity:
            score += 4
        if fb.weather_tag == weather_tag:
            score += 3

        if score < 10:
            continue

        if fb.liked:
            bonus += score
        else:
            bonus -= score

    return bonus
