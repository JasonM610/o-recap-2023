import boto3, os
import polars as pl
from dotenv import load_dotenv
from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_QUEUE_URL

basedir = os.path.abspath(".")
load_dotenv(os.path.join(basedir, ".env"))

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

s3 = session.resource("s3")
sqs = session.resource("sqs")
queue = sqs.Queue(AWS_QUEUE_URL)


def write_scores(user_id: int, scores_df: pl.DataFrame) -> None:
    scores_csv = scores_df.to_csv()
    s3.put_object(
        Body=scores_csv,
        Bucket=os.environ.get("BUCKET_NAME"),
        Key=f"scores/{user_id}.csv",
    )


def consume_messages() -> None:
    from app.utils.analytics import get_profile, insert_score_analytics
    from services.scores import build_scores_df

    while True:
        response = queue.receive_messages(MaxNumberOfMessages=1)

        for message in response:
            user_id = int(message.body)
            user = get_profile(user_id)
            message.delete()

            if user is not None:
                scores_df = build_scores_df(user_id, int(user["beatmaps_played"]))
                scores_df.write_csv(f"{user_id}.csv", separator=",")
                insert_score_analytics(user_id, scores_df)


consume_messages()
