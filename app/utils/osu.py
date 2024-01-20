from typing import Any, Dict, List, Union
from requests import RequestException
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from app.models import Score, User, BestScore
from config import CLIENT_ID, CLIENT_SECRET


class Osu:
    base_url = "https://osu.ppy.sh/api/v2/"
    token_url = "https://osu.ppy.sh/oauth/token"

    def __init__(self) -> None:
        self.session = self._create_session()

    def _create_session(self) -> OAuth2Session:
        client = BackendApplicationClient(client_id=CLIENT_ID, scope=["public"])
        session = OAuth2Session(client=client)
        session.fetch_token(
            token_url=self.token_url,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )

        return session

    def _make_request(
        self, method: str, url: str, body_params: Dict[str, Any] = None
    ) -> Any:
        try:
            response = self.session.request(
                method, f"{self.base_url}{url}", json=body_params
            )
            response.raise_for_status()
            return response.json()
        except TokenExpiredError:
            self.session = self._create_session()

            response = self.session.request(
                method, f"{self.base_url}{url}", json=body_params
            )
            response.raise_for_status()
            return response.json()
        except RequestException:
            raise

    def get_user(self, user: Union[int, str]) -> User:
        url = f"users/{user}"
        try:
            data = self._make_request("GET", url)
            return User(data)
        except RequestException:
            return None

    def get_beatmap_scores(self, user_id: int, beatmap_id: int) -> List[Score]:
        url = f"beatmaps/{beatmap_id}/scores/users/{user_id}/all"
        try:
            data = self._make_request("GET", url)
            return [
                Score(score, beatmap_id)
                for score in data.get("scores", [])
                if score["created_at"][:4] == "2023"
            ]
        except RequestException:
            return []

    def get_beatmap(self, beatmap_id: int) -> Dict[str, Any]:
        url = f"beatmaps/{beatmap_id}"
        try:
            data = self._make_request("GET", url)
            return data
        except RequestException:
            return None

    def get_beatmap_attribs(
        self, beatmap_id: int, body_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"beatmaps/{beatmap_id}/attributes"
        try:
            data = self._make_request("POST", url, body_params)
            return data.get("attributes")
        except RequestException:
            return None

    def get_best_scores(self, user_id: int) -> List[BestScore]:
        url = f"users/{user_id}/scores/best?mode=osu&limit=100"
        try:
            data = self._make_request("GET", url)
            return [
                BestScore(idx, score)
                for idx, score in enumerate(data)
                if score["created_at"][:4] == "2023"
            ]
        except RequestException as e:
            return []
