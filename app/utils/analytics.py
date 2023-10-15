import boto3, os
from typing import Any, Dict
from app.models import User, BestScore
from app.utils.osu import get_best_scores

sqs = boto3.client("sqs", region_name="us-east-2")
dynamo = boto3.resource("dynamodb")
profile_data = dynamo.Table("ProfileData")


def build_initial_data(user: User, best_scores: BestScore) -> Dict[str, Any]:
    best_scores_2023 = [
        {
            "performance_rank": score.performance_rank,
            "pp": score.pp,
            "accuracy": score.accuracy,
            "mods": score.mods,
            "letter_grade": score.letter_grade,
            "artist": score.artist,
            "title": score.title,
            "version": score.version,
            "list_url": score.list_url,
            "created_at": score.created_at,
        }
        for score in best_scores
        if score.created_at[:4] == "2023"
    ]

    return {
        "user_id": user.user_id,
        "username": user.username,
        "country_code": user.country_code,
        "avatar_url": user.avatar_url,
        "beatmaps_played_alltime": user.beatmaps_played_alltime,
        "achievements_2023": user.achievements_2023,
        "badges_2023": user.badges_2023,
        "playcount_2023": user.playcount_2023,
        "replays_watched_2023": user.replays_watched_2023,
        "best_scores_2023": best_scores_2023,
    }


def insert_data_and_enqueue(user: User) -> None:
    # need to add a check to see if user already exists

    best_scores = get_best_scores(user.user_id)
    initial_data = build_initial_data(user, best_scores)

    profile_data.put_item(Item=initial_data)

    message_body = {"UserID": str(user.user_id)}
    sqs.send_message(QueueUrl=os.environ.get("QUEUE_URL"), MessageBody=message_body)