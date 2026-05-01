#week_plan.py
from typing import List, Optional

from models import OutfitFeedback

from engine.generation.outfit_generation import generate_outfits


def generate_week_plan(
    garments,
    week_context,
    week_weather,
    feedback_list: Optional[List[OutfitFeedback]] = None,
):
    if feedback_list is None:
        feedback_list = []

    ordered_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    available_days = [day for day in ordered_days if day in week_context]

    week_plan = {}
    used_counts = {}
    used_by_category = {
        "top": {},
        "bottom": {},
        "shoes": {},
        "outerwear": {},
        "midlayer": {},
        "accessory": {},
    }

    for day in available_days:
        context = week_context[day]
        day_weather = week_weather.get(day, {})
        day_temp = day_weather.get("temp", 15)
        day_rain = day_weather.get("rain", False)

        synthetic_recent_outfits = [
            [g.id for g in planned_combo]
            for planned_combo in week_plan.values()
        ]

        outfits, _ = generate_outfits(
            garments=garments,
            occasion=context["occasion"],
            temp=day_temp,
            rain=day_rain,
            mood=context["mood"],
            activity=context["activity"],
            top_n=8,
            feedback_list=feedback_list,
            recent_outfits=synthetic_recent_outfits,
        )

        if not outfits:
            outfits, _ = generate_outfits(
                garments=garments,
                occasion=context["occasion"],
                temp=day_temp,
                rain=day_rain,
                mood=context["mood"],
                activity=context["activity"],
                top_n=5,
                feedback_list=feedback_list,
                recent_outfits=[],
            )

        if not outfits:
            week_plan[day] = []
            continue

        best_combo = None
        best_adjusted_score = None

        for score, combo in outfits:
            repetition_penalty_value = 0

            combo_ids = [g.id for g in combo]

            for g in combo:
                times_used_total = used_counts.get(g.id, 0)
                repetition_penalty_value += times_used_total * 12

                cat_used = used_by_category.get(g.category, {})
                times_used_in_category = cat_used.get(g.id, 0)

                if g.category == "top":
                    repetition_penalty_value += times_used_in_category * 14
                elif g.category == "bottom":
                    repetition_penalty_value += times_used_in_category * 12
                elif g.category == "shoes":
                    repetition_penalty_value += times_used_in_category * 16
                elif g.category == "outerwear":
                    repetition_penalty_value += times_used_in_category * 24
                elif g.category == "midlayer":
                    repetition_penalty_value += times_used_in_category * 9
                else:
                    repetition_penalty_value += times_used_in_category * 7

            for planned_combo in week_plan.values():
                planned_ids = [g.id for g in planned_combo]
                overlap = len(set(combo_ids) & set(planned_ids))

                if overlap >= 3:
                    repetition_penalty_value += 18
                elif overlap == 2:
                    repetition_penalty_value += 10
                elif overlap == 1:
                    repetition_penalty_value += 4

            if day != available_days[0]:
                previous_day = available_days[available_days.index(day) - 1]
                previous_combo = week_plan.get(previous_day, [])
                previous_by_category = {g.category: g.id for g in previous_combo}

                for g in combo:
                    if previous_by_category.get(g.category) == g.id:
                        if g.category in ["top", "bottom", "shoes", "outerwear"]:
                            repetition_penalty_value += 16
                        else:
                            repetition_penalty_value += 6

            adjusted_score = score - repetition_penalty_value

            if best_combo is None or adjusted_score > best_adjusted_score:
                best_combo = combo
                best_adjusted_score = adjusted_score

        if best_combo:
            week_plan[day] = best_combo

            for g in best_combo:
                used_counts[g.id] = used_counts.get(g.id, 0) + 1

                if g.category not in used_by_category:
                    used_by_category[g.category] = {}

                used_by_category[g.category][g.id] = (
                    used_by_category[g.category].get(g.id, 0) + 1
                )
        else:
            week_plan[day] = []

    return week_plan
