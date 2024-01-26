from app.utils.queue import SQS
from app.utils.db import Dynamo
from services.analytics import Analytics


def consume_messages() -> None:
    db, sqs = Dynamo(), SQS()
    while True:
        response = sqs.queue.receive_messages(MaxNumberOfMessages=1)

        for message in response:
            user_id = int(message.body)
            user = db.get_profile_from_id(user_id)

            if user:
                analytics = Analytics(user)
                analytics.write_scores()
                db.insert_analytics(user_id, analytics.get_analytics())

            message.delete()


if __name__ == "__main__":
    consume_messages()
