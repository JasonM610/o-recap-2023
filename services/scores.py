import boto3, os, time
import polars as pl
from typing import Dict, Any
from app.utils.osu import get_beatmap, get_beatmap_attribs, get_beatmap_scores
from services.beatmaps import collect_beatmap_ids

dynamo = boto3.resource(
    "dynamodb",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("REGION"),
)
table = dynamo.Table("BeatmapData")


def build_scores_df(user_id: int, beatmaps_played: int) -> pl.DataFrame:
    """Collects all of a user's 2023 scores and related data used in analytics.

    Args:
        user_id (int): A user's ID
        beatmaps_played (int): The amount of beatmaps the user has played

    Returns:
        pl.DataFrame: A DataFrame containing every submitted score from a user
    """
    scores = []

    for beatmap_id in collect_beatmap_ids(user_id, beatmaps_played):
        start = time.time()
        beatmap_data = get_beatmap(beatmap_id)
        if beatmap_data in ["graveyard", "wip", "pending"]:
            continue

        for score in get_beatmap_scores(user_id, beatmap_id):
            mods = set(score.mods)
            if mods & {"EZ", "HR", "HT", "DT", "FL"}:
                rate = 1.50 if "DT" in mods else 0.75 if "HT" in mods else 1.00
                cs_scale = 1.30 if "HR" in mods else 0.50 if "EZ" in mods else 1.00

                beatmap_attribs = get_beatmap_attribs(beatmap_id, {"mods": score.mods})
                beatmap_data.update(
                    {
                        "difficulty_rating": beatmap_attribs["star_rating"],
                        "hit_length": int(beatmap_data["hit_length"] * (1 / rate)),
                        "bpm": int(beatmap_data["bpm"] * rate),
                        "ar": beatmap_attribs["approach_rate"],
                        "accuracy": beatmap_attribs["overall_difficulty"],
                        "cs": max(10, beatmap_data["cs"] * cs_scale),
                    }
                )

            score_dict = {
                **score.to_dict(),
                "star_rating": beatmap_data["difficulty_rating"],
                "length": beatmap_data["hit_length"],
                "bpm": beatmap_data["bpm"],
                "ar": beatmap_data["ar"],
                "od": beatmap_data["accuracy"],
                "cs": beatmap_data["cs"],
                "set_owner": beatmap_data["user_id"],
            }

            score_dict["mods"] = ",".join(score_dict["mods"])
            scores.append(score_dict)

    return pl.DataFrame(scores)


def fetch_beatmap_data(beatmap_id: int) -> Dict[str, Any]:
    response = table.get_item(Key={"beatmap_id": beatmap_id})

    if "Item" not in response:
        return None

    return response["Item"]
