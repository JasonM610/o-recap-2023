import os
from datetime import datetime
from typing import Any, Dict, List
from requests import Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
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


def make_request(url: str) -> Response:
    return session.request("GET", f"{base_url}/{url}")


def get_user_data(user_id: int, mode: str) -> User:
    url = f"users/{user_id}/{mode}"
    data = make_request(url).json()

    badges_2023 = filter_badges(data)
    playcount_2023 = filter_playcount(data)
    replays_2023 = filter_replays(data)

    return User(
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


def get_best_scores(user_id: int, mode: str) -> List[UserBestScore]:
    url = f"users/{user_id}/scores/best?mode={mode}&limit=100"
    data = make_request(url).json()
    score_data = []

    for ind, play in enumerate(data):
        if play["created_at"][:4] == "2023":
            score_data.append(
                UserBestScore(
                    score_id=play["id"],
                    user_id=play["user_id"],
                    beatmap_id=play["beatmap"]["id"],
                    accuracy=round(play["accuracy"], 4),
                    pp=play["pp"],
                    mods=",".join(play["mods"]),
                    rank=ind + 1,
                    score=play["score"],
                    letter_grade=play["rank"],
                    created_at=play["created_at"],
                    mode=mode,
                )
            )

    return score_data


def filter_badges(data: List[Dict[str, Any]]) -> List[str]:
    return [
        badge["awarded_at"]
        for badge in data["badges"]
        if badge["awarded_at"][:4] == "2023"
    ]


def filter_playcount(data: List[Dict[str, Any]]) -> List[int]:
    return [
        playcount["count"]
        for playcount in data["monthly_playcounts"]
        if playcount["start_date"][:4] == "2023"
    ]


def filter_replays(data: List[Dict[str, Any]]) -> List[int]:
    return [
        replay["count"]
        for replay in data["replays_watched_counts"]
        if replay["start_date"][:4] == "2023"
    ]
