from typing import Any, Dict, List, Union
from requests import RequestException
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from app.models import Score, User, BestScore
from config import CLIENT_ID, CLIENT_SECRET

base_url = "https://osu.ppy.sh/api/v2/"
token_url = "https://osu.ppy.sh/oauth/token"


def create_session() -> OAuth2Session:
    client = BackendApplicationClient(client_id=CLIENT_ID, scope=["public"])
    session = OAuth2Session(client=client)
    session.fetch_token(
        token_url=token_url, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

    return session


def make_request(method: str, url: str, body_params: Dict[str, Any] = None) -> Any:
    try:
        response = session.request(method, f"{base_url}{url}", json=body_params)
        response.raise_for_status()
        return response.json()
    except TokenExpiredError:
        new_session = create_session()

        response = new_session.request(method, f"{base_url}{url}", json=body_params)
        response.raise_for_status()
        return response.json()
    except RequestException:
        raise


def get_user(user: Union[int, str]) -> User:
    url = f"users/{user}"
    try:
        data = make_request("GET", url)
        return User(data)
    except RequestException:
        return None


def get_beatmap_scores(user_id: int, beatmap_id: int) -> List[Score]:
    url = f"beatmaps/{beatmap_id}/scores/users/{user_id}/all"
    try:
        data = make_request("GET", url)
        return [
            Score(score, beatmap_id)
            for score in data.get("scores", [])
            if score["created_at"][:4] == "2023"
        ]
    except RequestException:
        return []


def get_beatmap(beatmap_id: int) -> Dict[str, Any]:
    url = f"beatmaps/{beatmap_id}"
    try:
        data = make_request("GET", url)
        return data
    except RequestException:
        return None


def get_beatmap_attribs(beatmap_id: int, body_params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"beatmaps/{beatmap_id}/attributes"
    try:
        data = make_request("POST", url, body_params)
        return data.get("attributes")
    except RequestException:
        return None


def get_best_scores(user_id: int) -> List[BestScore]:
    url = f"users/{user_id}/scores/best?mode=osu&limit=100"
    try:
        data = make_request("GET", url)
        return [BestScore(idx, play) for idx, play in enumerate(data)]
    except RequestException as e:
        return []


session = create_session()
