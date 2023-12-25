import boto3, os, time
import polars as pl
from typing import Any, Dict, List
from boto3.dynamodb.conditions import Key
from app.models import User, BestScore
from app.utils.osu import get_user, get_beatmap, get_best_scores
from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_QUEUE_URL


access_key = os.environ.get("AWS_ACCESS_KEY")
secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("REGION")

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

sqs = session.resource("sqs")
queue = sqs.Queue(AWS_QUEUE_URL)
dynamo = session.resource("dynamodb")
table = dynamo.Table("ProfileData")


def insert_user_and_enqueue(user: User) -> None:
    if get_profile(user.user_id) is not None:
        return

    best_scores = get_best_scores(user.user_id)
    initial_data = build_initial_data(user, best_scores)

    table.put_item(Item=initial_data)
    queue.send_message(MessageBody=str(user.user_id))


def get_profile(user_id: int) -> Dict[str, Any]:
    response = table.get_item(Key={"user_id": user_id})

    if "Item" not in response:
        return None

    return response["Item"]


def get_id_from_username(username: str) -> int:
    response = table.query(
        IndexName="username-index",
        KeyConditionExpression=Key("username_search").eq(username.lower()),
    )

    if "Items" not in response or len(response["Items"]) == 0:
        return -1

    return int(response["Items"][0]["user_id"])


def build_initial_data(user: User, best_scores: List[BestScore]) -> Dict[str, Any]:
    best_scores_2023 = [
        score.to_dict() for score in best_scores if score.created_at[:4] == "2023"
    ]

    initial_data = user.to_dict()
    initial_data["best_scores_2023"] = best_scores_2023

    return initial_data


def insert_score_analytics(user_id: int, scores: pl.DataFrame) -> None:
    def get_2023_pp() -> str:
        # filter scores list to ranked maps, get highest pp score on each map
        best_scores = (
            scores.filter(pl.col("ranked") == 1)
            .group_by("beatmap_id")
            .agg(pl.col("pp").max())
        )

        # assign rank to each score based on pp value, return weighted sum
        score_ranking = best_scores["pp"].rank(method="ordinal", descending=True)
        return str(round((best_scores["pp"] * (0.95 ** (score_ranking - 1))).sum(), 3))

    def get_highest_sr_pass() -> Dict[str, Any]:
        passes = scores.filter(~pl.col("mods").str.contains("NF")).filter(
            pl.col("ranked") == 1
        )

        if passes.is_empty():
            return {}

        best_pass = passes[passes["star_rating"].arg_max()]
        beatmap_id = best_pass["beatmap_id"][0]
        beatmap_data = get_beatmap(beatmap_id)

        return {
            "beatmap_id": best_pass["beatmap_id"][0],
            "artist": beatmap_data["beatmapset"]["artist"],
            "title": beatmap_data["beatmapset"]["title"],
            "version": beatmap_data["version"],
            "mods": best_pass["mods"][0],
            "acc": str(round(best_pass["accuracy"][0], 4)),
            "pp": round(best_pass["pp"][0]),
            "letter_grade": best_pass["letter_grade"][0],
            "combo": best_pass["max_combo"][0],
            "max_combo": beatmap_data["max_combo"],
            "sr": str(round(best_pass["star_rating"][0], 2)),
            "background_url": beatmap_data["beatmapset"]["covers"]["card@2x"],
        }

    def get_averages() -> Dict[str, Any]:
        return {
            "ar": str(round(scores["ar"].mean(), 2)),
            "cs": str(round(scores["cs"].mean(), 1)),
            "bpm": str(int(scores["bpm"].mean())),
            "acc": str(round(scores["accuracy"].mean(), 4)),
            "len": str(int(scores["length"].mean())),
            "sr": str(round(scores["star_rating"].mean(), 2)),
        }

    def get_aggregates() -> Dict[str, Any]:
        grade_counts = [
            scores.filter(pl.col("letter_grade") == grade).select(pl.count()).item()
            for grade in ["XH", "SH", "X", "S", "A", "B", "C", "D"]
        ]

        map_counts = scores["set_owner"].value_counts(sort=True).head(3)
        map_counts = map_counts.with_columns(
            map_counts["set_owner"]
            .apply(get_user)
            .apply(lambda user: user.username)
            .alias("username")
        )

        mod_counts = scores["mods"].value_counts(sort=True).head(3)

        return {
            "scores": scores.select(pl.count()).item(),
            "ranked_score": scores["score"].sum(),
            "letter_grades": grade_counts,
            "most_played_mappers": map_counts.to_dict(as_series=False),
            "most_played_mods": mod_counts.to_dict(as_series=False),
        }

    analytics = (
        {}
        if scores.is_empty()
        else {
            "year_pp": get_2023_pp(),
            "highest_sr_pass": get_highest_sr_pass(),
            "avg": get_averages(),
            "agg": get_aggregates(),
        }
    )

    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET analytics = :r",
        ExpressionAttributeValues={":r": analytics},
    )
