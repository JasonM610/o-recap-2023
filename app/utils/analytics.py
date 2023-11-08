import boto3, os
import polars as pl
from typing import Any, Dict, List
from app.models import User, BestScore
from app.utils.osu import get_user, get_best_scores

# sqs = boto3.client("sqs", region_name=os.environ.get("REGION"))
# s3 = boto3.client("s3")
# bucket = s3.Bucket(osu.environ.get("BUCKET_NAME"))
dynamo = boto3.resource(
    "dynamodb",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("REGION"),
)
table = dynamo.Table("ProfileData")


def insert_user_and_enqueue(user: User) -> None:
    if get_profile(user.user_id) is not None:
        return

    best_scores = get_best_scores(user.user_id)
    initial_data = build_initial_data(user, best_scores)
    table.put_item(Item=initial_data)

    message_body = {"UserID": str(user.user_id)}
    # sqs.send_message(QueueUrl=os.environ.get("QUEUE_URL"), MessageBody=message_body)


def get_profile(user_id: int) -> Dict[str, Any]:
    response = table.get_item(Key={"user_id": user_id})

    if "Item" not in response:
        return None

    return response["Item"]


def build_initial_data(user: User, best_scores: List[BestScore]) -> Dict[str, Any]:
    best_scores_2023 = [
        score.to_dict() for score in best_scores if score.created_at[:4] == "2023"
    ]

    initial_data = user.to_dict()
    initial_data["best_scores_2023"] = best_scores_2023

    return initial_data


def insert_score_analytics(user_id: int, scores: pl.DataFrame) -> None:
    def get_2023_pp() -> int:
        best_scores = scores.group_by("beatmap_id").agg(pl.col("pp").max())
        score_ranking = best_scores["pp"].rank(method="ordinal", descending=True)

        year_pp = (best_scores["pp"] * (0.95 ** (score_ranking - 1))).sum()

        return round(year_pp, 3)

    def get_highest_sr_pass() -> Dict[str, Any]:
        passes = scores.filter(~scores["mods"].str.contains("NF"))

        if passes.is_empty():
            return {}

        best_pass = passes[passes["star_rating"].arg_max()]

        return {
            "beatmap_id": best_pass["beatmap_id"][0],
            "mods": best_pass["mods"][0],
            "star_rating": round(best_pass["star_rating"][0], 2),
        }

    def get_habits() -> int:
        map_counts = scores["set_owner"].value_counts(sort=True).head(3)
        mod_counts = scores["mods"].value_counts(sort=True).head(3)

        return {
            "average_bpm": int(scores["bpm"].mean()),
            "average_len": int(scores["length"].mean()),
            "favorite_ar": scores["ar"].mode()[0],
            "favorite_cs": scores["cs"].mode()[0],
            "most_played_mapper": get_user(scores["set_owner"].mode()[0]).username,
            "most_played_mods": mod_counts.to_dict(as_series=False),
        }

    analytics = {
        "2023_pp": get_2023_pp(),
        "highest_sr_pass": get_highest_sr_pass(),
        "habits": get_habits(),
    }
    print(analytics)
