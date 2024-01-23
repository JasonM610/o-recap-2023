import os
import polars as pl
from app.utils.queue import SQS
from app.utils.db import Dynamo
from services.analytics import Analytics


def write_scores(user_id: int, scores_df: pl.DataFrame) -> None:
    scores_csv = scores_df.to_csv()
    s3.put_object(
        Body=scores_csv,
        Bucket=os.environ.get("BUCKET_NAME"),
        Key=f"scores/{user_id}.csv",
    )


def consume_messages() -> None:
    db, sqs = Dynamo(), SQS()
    while True:
        response = sqs.queue.receive_messages(MaxNumberOfMessages=1)

        for message in response:
            user_id = int(message.body)
            user = db.get_profile_from_id(user_id)

            if user is not None:
                analytics = Analytics(user)
                analytics.write_scores()
                db.insert_analytics(user_id, analytics.get_analytics())
                message.delete()


if __name__ == "__main__":
    consume_messages()
