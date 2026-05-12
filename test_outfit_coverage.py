import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from storage_cloud import garment_from_dict
import engine.recommender  # rompe el import circular: recommender debe cargarse antes que outfit_generation
from engine.generation.outfit_generation import generate_outfits
from constants import OCCASION_OPTIONS, MOOD_OPTIONS

USER_ID = "27f1ddde-d806-40ad-ac3d-5339e3b9d19a"

sb = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

OCCASIONS = [o for o in OCCASION_OPTIONS if o not in ["gala", "matrimonio"]]
MOODS = [m for m in MOOD_OPTIONS]
TEMPS = [5, 10, 15, 20, 25]
RAIN_OPTIONS = [False, True]


def run():
    response = sb.table("garments").select("*").eq("user_id", USER_ID).execute()
    garments = [garment_from_dict(item) for item in (response.data or [])]
    print(f"Closet cargado: {len(garments)} prendas\n")

    results = []

    for occasion in OCCASIONS:
        for mood in MOODS:
            for temp in TEMPS:
                for rain in RAIN_OPTIONS:
                    try:
                        outfits, missing = generate_outfits(
                            garments=garments,
                            occasion=occasion,
                            temp=temp,
                            rain=rain,
                            mood=mood,
                            activity="normal",
                            top_n=3,
                            feedback_list=[],
                            recent_outfits=[],
                        )
                        n = len(outfits)
                        results.append({
                            "ocasion": occasion,
                            "mood": mood,
                            "temp": temp,
                            "lluvia": rain,
                            "outfits": n,
                            "missing": ",".join(missing) if missing else "-",
                            "ok": n >= 3,
                        })
                    except Exception as e:
                        results.append({
                            "ocasion": occasion,
                            "mood": mood,
                            "temp": temp,
                            "lluvia": rain,
                            "outfits": f"ERR",
                            "missing": str(e)[:40],
                            "ok": False,
                        })

    total = len(results)
    failures = sum(1 for r in results if not r["ok"])

    # Tabla completa
    W_OC, W_MO, W_MI = 20, 10, 20
    sep = "-" * (W_OC + W_MO + 6 + 7 + 9 + 3 + W_MI + 4)
    header = (
        f"{'Ocasion':<{W_OC}} {'Mood':<{W_MO}} {'Temp':>5} {'Lluvia':>6} "
        f"{'Outfits':>8}   {'Missing':<{W_MI}}"
    )
    print(header)
    print(sep)

    prev_occasion = None
    for r in results:
        if r["ocasion"] != prev_occasion:
            if prev_occasion is not None:
                print(sep)
            prev_occasion = r["ocasion"]

        flag = "  " if r["ok"] else "!!"
        lluvia = "si" if r["lluvia"] else "no"
        print(
            f"{r['ocasion']:<{W_OC}} {r['mood']:<{W_MO}} {r['temp']:>5} "
            f"{lluvia:>6} {str(r['outfits']):>8} {flag} {r['missing']:<{W_MI}}"
        )

    print(sep)
    print(f"\nTotal: {total}  |  OK: {total - failures}  |  Fallos (<3): {failures}")


if __name__ == "__main__":
    run()
