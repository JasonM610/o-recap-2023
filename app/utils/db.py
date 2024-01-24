import boto3
from boto3.dynamodb.conditions import Key
from typing import Any, Dict
from app.utils.queue import SQS
from config import (
    AWS_ACCESS_KEY,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    AWS_PROFILE_TABLE,
)


class Dynamo:
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    dynamo = session.resource("dynamodb")
    table = dynamo.Table(AWS_PROFILE_TABLE)

    def get_profile(self, user_input: str) -> Dict[str, Any]:
        return (
            self.get_profile_from_id(int(user_input))
            if user_input.isdigit()
            else self.get_profile_from_username(user_input)
        )

    def get_profile_from_id(self, user_id: int) -> Dict[str, Any]:
        response = self.table.get_item(Key={"user_id": user_id})

        if "Item" not in response:
            return {}

        return response["Item"]

    def get_profile_from_username(self, username: str) -> Dict[str, Any]:
        response = self.table.query(
            IndexName="username-index",
            KeyConditionExpression=Key("username_search").eq(username.lower()),
        )

        if "Items" not in response or len(response["Items"]) == 0:
            return {}

        return response["Items"][0]

    def insert_profile(self, user_profile: Dict[str, Any]) -> None:
        self.table.put_item(Item=user_profile)

        sqs = SQS()
        sqs.queue.send_message(
            MessageBody=str(user_profile["user_id"]), MessageGroupId="o-recap-2023"
        )

    def insert_analytics(self, user_id: int, analytics: Dict[str, Any]) -> None:
        self.table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="SET analytics = :r",
            ExpressionAttributeValues={":r": analytics},
        )
