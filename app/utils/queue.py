import boto3
from config import (
    AWS_ACCESS_KEY,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    AWS_QUEUE_URL,
)


class SQS:
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    sqs = session.resource("sqs")
    queue = sqs.Queue(AWS_QUEUE_URL)

    def get_queue_size(self) -> int:
        return int(self.queue.attributes["ApproximateNumberOfMessages"]) + int(
            self.queue.attributes["ApproximateNumberOfMessagesNotVisible"]
        )
