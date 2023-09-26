import os
from typing import Any, List, Tuple, Union
from requests import RequestException, Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from app.models import Beatmap, Score, User, BestScore
from app.utils.beatmaps import fetch_beatmaps_from_profile


client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

base_url = "https://osu.ppy.sh/api/v2/"
token_url = "https://osu.ppy.sh/oauth/token"


client = BackendApplicationClient(client_id=client_id, scope=["public"])
session = OAuth2Session(client=client)
token = session.fetch_token(
    token_url=token_url, client_id=client_id, client_secret=client_secret
)


def make_request(url: str) -> Response:
    try:
        response = session.request("GET", f"{base_url}{url}")
        return response
    except RequestException as e:
        raise


def fetch_data(url: str) -> Any:
    try:
        response = make_request(url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise


def get_user_data(user: Union[int, str], mode: str) -> User:
    url = f"users/{user}/{mode}"
    try:
        data = fetch_data(url)
    except RequestException as e:
        return None

    return User(data, mode)


def get_best_scores(
    user_id: int, mode: str
) -> Tuple[List[BestScore], List[Score], List[Beatmap]]:
    url = f"users/{user_id}/scores/best?mode={mode}&limit=100"
    try:
        data = fetch_data(url)
    except RequestException as e:
        return [], [], []

    best_scores = [BestScore(idx, play, mode) for idx, play in enumerate(data)]
    scores = [Score(play, mode) for play in data]
    beatmaps = [Beatmap(play, mode) for play in data]

    return best_scores, scores, beatmaps


def get_scores(
    user_id: int, beatmap_id: int, mode: str
) -> Tuple[List[Score], List[Beatmap]]:
    url = f"beatmaps/{beatmap_id}/scores/users/{user_id}/all"
    try:
        data = fetch_data(url)
    except RequestException as e:
        return [], []

    beatmap = Beatmap(data, mode)
    scores = [Score(play, mode) for play in data]

    return scores, beatmap
