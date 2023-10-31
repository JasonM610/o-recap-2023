import boto3, os
from typing import Any, Dict, List
from app.models import User, Score, BestScore
from app.utils.osu import get_best_scores

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


def insert_score_analytics(user_id: int, scores: List[Score]) -> None:
    pass
