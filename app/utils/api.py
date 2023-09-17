import os, json, sys, datetime
from typing import List, Union
from oauthlib.oauth2 import BackendApplicationClient
from requests import Response
from requests_oauthlib import OAuth2Session
from app.models import User, UserBestScore

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

base_url = "https://osu.ppy.sh/api/v2"
token_url = "https://osu.ppy.sh/oauth/token"


client = BackendApplicationClient(client_id=client_id, scope=["public"])
session = OAuth2Session(client=client)
token = session.fetch_token(
    token_url=token_url, client_id=client_id, client_secret=client_secret
)


def get_user_data(user_id: int, mode: str) -> User:
    url = f"users/{user_id}/{mode}"
    data = send_request(url).json()

    badges_2023 = [
        badge["awarded_at"]
        for badge in data["badges"]
        if badge["awarded_at"][:4] == "2023"
    ]

    playcount_2023 = [
        pc["count"]
        for pc in data["monthly_playcounts"]
        if pc["start_date"][:4] == "2023"
    ]

    replays_2023 = [
        replay["count"]
        for replay in data["replays_watched_counts"]
        if replay["start_date"][:4] == "2023"
    ]

    user_data = User(
        user_id=data["id"],
        user_name=data["username"],
        country_code=data["country_code"],
        avatar_url=data["avatar_url"],
        beatmaps_played_alltime=data["beatmap_playcounts_count"],
        badges_2023=len(badges_2023),
        playcount_2023=sum(playcount_2023),
        replays_watched_2023=sum(replays_2023),
        mode=mode,
    )

    return user_data


def get_best_scores(user_id: int, mode: str) -> List[UserBestScore]:
    url = f"users/{user_id}/scores/best?mode={mode}&limit=100"
    data = send_request(url).json()
    score_data = []

    for ind, play in enumerate(data):
        score = UserBestScore(
            score_id=play["id"],
            user_id=play["user_id"],
            beatmap_id=play["beatmap"]["id"],
            accuracy=round(play["accuracy"], 4),
            pp=play["pp"],
            mods=",".join(play["mods"]),
            rank=ind + 1,
            score=play["score"],
            letter_grade=play["rank"],
            created_at=datetime.strptime(play["created_at"]),
            mode=mode,
        )
        if score["created_at"].year == 2023:
            score_data.append(score)

    return score_data


def send_request(url: str) -> Response:
    return session.request("GET", f"{base_url}/{url}")


data = get_user_data(4394718, "osu")
for key, value in data.__dict__.items():
    if not key.startswith("_"):
        print(f"{key}: {value}")
