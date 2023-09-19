import os
from datetime import datetime
from typing import Any, Dict, List, Tuple
from requests import Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from app.models import Beatmap, Score, User, BestScore

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

    return User(data, mode)


def get_best_scores(
    user_id: int, mode: str
) -> Tuple[List[Score], List[Beatmap], List[BestScore]]:
    url = f"users/{user_id}/scores/best?mode={mode}&limit=100"
    data = make_request(url).json()

    score_data = [Score(play, mode) for play in data]
    beatmap_data = [Beatmap(play, mode) for play in data]
    top_play_data = [BestScore(idx, play, mode) for idx, play in enumerate(data)]

    return score_data, beatmap_data, top_play_data
