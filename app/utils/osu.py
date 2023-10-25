import os
from typing import Any, Dict, List, Union
from requests import RequestException, Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from app.models import Beatmap, Score, User, BestScore


client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

base_url = "https://osu.ppy.sh/api/v2/"
token_url = "https://osu.ppy.sh/oauth/token"

client = BackendApplicationClient(client_id=client_id, scope=["public"])
session = OAuth2Session(client=client)
token = session.fetch_token(
    token_url=token_url, client_id=client_id, client_secret=client_secret
)


def make_request(method: str, url: str, body_params: Dict[str, Any] = None) -> Any:
    try:
        response = session.request(method, f"{base_url}{url}", json=body_params)
        return response.json()
    except RequestException as e:
        raise


def get_user(user: Union[int, str]) -> User:
    url = f"users/{user}"
    try:
        data = make_request("GET", url)
        return User(data)
    except RequestException as e:
        return None


def get_beatmap(beatmap_id: int) -> Beatmap:
    url = f"beatmaps/{beatmap_id}"
    try:
        data = make_request("GET", url)
        return Beatmap(data)
    except RequestException as e:
        return None


def get_beatmap_scores(user_id: int, beatmap_id: int) -> List[Score]:
    url = f"beatmaps/{beatmap_id}/scores/users/{user_id}/all"
    try:
        data = make_request("GET", url)
        return [Score(play) for play in data]
    except RequestException as e:
        return []


def get_beatmap_stats(beatmap_id: int, body_params: Dict[str, Any]) -> Beatmap:
    url = f"beatmaps/{beatmap_id}/attributes"
    try:
        data = make_request("POST", url, body_params)
        return data
    except RequestException as e:
        return None


def get_best_scores(user_id: int) -> List[BestScore]:
    url = f"users/{user_id}/scores/best?mode=osu&limit=100"
    try:
        data = make_request("GET", url)
        return [BestScore(idx, play) for idx, play in enumerate(data)]
    except RequestException as e:
        return []
