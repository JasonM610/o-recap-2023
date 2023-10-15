import os, json
from typing import Any, List, Union
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


def get_user_data(user: Union[int, str]) -> User:
    url = f"users/{user}"
    try:
        data = fetch_data(url)
    except RequestException as e:
        return None

    return User(data)


def get_beatmap_data(beatmap_id: int) -> Beatmap:
    url = f"beatmaps/{beatmap_id}"
    try:
        data = fetch_data(url)
    except RequestException as e:
        return None

    obj = json.dumps(data, indent=4)
    with open("beatmap.json", "w") as outfile:
        outfile.write(obj)

    return Beatmap(data)


def get_beatmap_scores(user_id: int, beatmap_id: int) -> List[Score]:
    url = f"beatmaps/{beatmap_id}/scores/users/{user_id}/all"
    try:
        data = fetch_data(url)
    except RequestException as e:
        return []

    obj = json.dumps(data, indent=4)
    with open("score.json", "w") as outfile:
        outfile.write(obj)

    scores = [Score(play) for play in data]

    return scores


def get_best_scores(user_id: int) -> List[BestScore]:
    url = f"users/{user_id}/scores/best?mode=osu&limit=100"
    try:
        data = fetch_data(url)
    except RequestException as e:
        return [], [], []

    best_scores = [BestScore(idx, play) for idx, play in enumerate(data)]

    return best_scores
