import boto3, os
import pandas as pd
from typing import Any, Dict, List
from app.models import User, BestScore
from app.utils.osu import get_best_scores

# sqs = boto3.client("sqs", region_name="us-east-2")
# s3 = boto3.client("s3")
# bucket = s3.Bucket("your-2023-recap")
dynamo = boto3.resource(
    "dynamodb",
    aws_access_key_id="nope",
    aws_secret_access_key="nope",
    region_name="us-east-2",
)
table = dynamo.Table("ProfileData")


def build_initial_data(user: User, best_scores: List[BestScore]) -> Dict[str, Any]:
    best_scores_2023 = [
        {
            "performance_rank": str(score.performance_rank),
            "pp": str(score.pp),
            "accuracy": str(score.accuracy),
            "mods": score.mods,
            "letter_grade": str(score.letter_grade.name),
            "artist": score.artist,
            "title": score.title,
            "version": score.version,
            "list_url": score.list_url,
            "created_at": str(score.created_at),
        }
        for score in best_scores
        if score.created_at[:4] == "2023"
    ]

    return {
        "user_id": user.user_id,
        "username": user.username,
        "country_code": user.country_code,
        "avatar_url": user.avatar_url,
        "beatmaps_played_alltime": str(user.beatmaps_played_alltime),
        "achievements_2023": str(user.achievements_2023),
        "badges_2023": str(user.badges_2023),
        "playcount_2023": str(user.playcount_2023),
        "replays_watched_2023": str(user.replays_watched_2023),
        "best_scores_2023": best_scores_2023,
    }


def get_profile(user_id: int) -> Dict[str, Any]:
    response = table.get_item(Key={"user_id": user_id})

    if "Item" in response is None:
        return None

    return response["Item"]


def insert_user_and_enqueue(user: User) -> None:
    if get_profile(user.user_id) is not None:
        return

    best_scores = get_best_scores(user.user_id)
    initial_data = build_initial_data(user, best_scores)
    table.put_item(Item=initial_data)

    message_body = {"UserID": str(user.user_id)}
    # sqs.send_message(QueueUrl=os.environ.get("QUEUE_URL"), MessageBody=message_body)
