import polars as pl
from typing import Dict, Any
from app.utils.osu import get_beatmap, get_beatmap_attribs, get_beatmap_scores
from services.beatmaps import collect_beatmap_ids


def build_scores_df(user_id: int, beatmaps_played: int) -> pl.DataFrame:
    def process_score() -> Dict[str, Any]:
        score_dict = score.to_dict() | {
            "mods": ",".join(score.mods),
            "star_rating": beatmap_data["difficulty_rating"],
            "length": beatmap_data["hit_length"],
            "bpm": beatmap_data["bpm"],
            "ar": beatmap_data["ar"],
            "od": beatmap_data["accuracy"],
            "cs": beatmap_data["cs"],
            "ranked": beatmap_data["ranked"],
            "set_owner": beatmap_data["user_id"],
        }

        mods = set(score.mods) - set(["HD", "NF", "SD", "PF", "SO"])
        if mods & {"EZ", "HR", "HT", "DT", "NC", "FL"}:
            rate = 1.5 if "DT" in mods or "NC" in mods else 0.75 if "HT" in mods else 1
            cs_scale = 1.3 if "HR" in mods else 0.5 if "EZ" in mods else 1

            # eventually store modded attributes inside table -> reduce api calls
            beatmap_attribs = get_beatmap_attribs(beatmap_id, {"mods": score.mods})
            if beatmap_attribs is not None:
                score_dict.update(
                    {
                        "star_rating": round(beatmap_attribs["star_rating"], 2),
                        "length": int(beatmap_data["hit_length"] * (1 / rate)),
                        "bpm": int(beatmap_data["bpm"] * rate),
                        "ar": round(beatmap_attribs["approach_rate"], 2),
                        "od": round(beatmap_attribs["overall_difficulty"], 2),
                        "cs": min(10, round(beatmap_data["cs"] * cs_scale, 2)),
                    }
                )

        return score_dict

    scores = []

    for beatmap_id in collect_beatmap_ids(user_id, beatmaps_played):
        beatmap_data = get_beatmap(beatmap_id)

        if (
            beatmap_data is None
            or beatmap_data.get("status") in ["graveyard", "wip", "pending"]
            or beatmap_data.get("mode") != "osu"
        ):
            continue

        for score in get_beatmap_scores(user_id, beatmap_id):
            scores.append(process_score())

    return pl.DataFrame(scores)
