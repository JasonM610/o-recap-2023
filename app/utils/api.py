import os
from datetime import datetime
from typing import Any, Dict, List, Tuple
from requests import Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from app.models import Beatmap, Score, User, UserBestScore
from app.utils.enums import Mode

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

    return build_user(data, badges_2023, playcount_2023, replays_2023, mode)


def get_best_scores(
    user_id: int, mode: str
) -> Tuple(List[Score], List[Beatmap], List[UserBestScore]):
    url = f"users/{user_id}/scores/best?mode={mode}&limit=120"  # ? might not work
    data = make_request(url).json()

    score_data = [build_score(play, mode) for play in data]
    beatmap_data = [build_beatmap(play, mode) for play in data]
    top_play_data = [build_top_play(idx, play, mode) for idx, play in enumerate(data)]

    return score_data, beatmap_data, top_play_data


def build_user(
    player: Dict[str, Any],
    badges: List[str],
    playcount: List[int],
    replays: List[int],
    mode: Mode,
) -> User:
    return User(
        user_id=player["id"],
        user_name=player["username"],
        country_code=player["country_code"],
        avatar_url=player["avatar_url"],
        beatmaps_played_alltime=player["beatmap_playcounts_count"],
        badges_2023=len(badges),
        playcount_2023=sum(playcount),
        replays_watched_2023=sum(replays),
        mode=mode,
    )


def build_score(play: Dict[str, Any], mode: Mode) -> Score:
    return Score(
        score_id=play["id"],
        user_id=play["user_id"],
        beatmap_id=play["beatmap"]["id"],
        accuracy=round(play["accuracy"], 4),
        pp=play["pp"],
        mods=",".join(play["mods"]),
        score=play["score"],
        letter_grade=play["rank"],
        max_combo=play["max_combo"],
        count_300=play["statistics"]["count_300"],
        count_100=play["statistics"]["count_100"],
        count_50=play["statistics"]["count_50"],
        count_miss=play["statistics"]["count_miss"],
        passed=play["passed"],
        created_at=play["created_at"],
        mode=mode,
    )


def build_beatmap(play: Dict[str, Any], mode: Mode) -> Beatmap:
    map = play["beatmap"]
    set = play["beatmapset"]
    return Beatmap(
        beatmap_id=map["id"],
        beatmapset_id=map["beatmapset_id"],
        artist=set["artist"],
        title=set["title"],
        version=map["version"],
        creator=set["creator"],
        play_count=map["playcount"],
        status=map["status"],
        difficulty_rating=map["difficulty_rating"],
        length=map["hit_length"],
        bpm=map["bpm"],
        approach_rate=map["ar"],
        circle_size=map["cs"],
        overall_difficulty=map["accuracy"],
        hp_drain=map["drain"],
        cover_url=set["covers"]["cover"],
        list_url=set["covers"]["list"],
        mode=map["mode"],
    )


def build_top_play(idx: int, play: Dict[str, Any], mode: Mode) -> UserBestScore:
    return UserBestScore(
        score_id=play["id"],
        user_id=play["user_id"],
        beatmap_id=play["beatmap"]["id"],
        performance_rank=idx + 1,
    )


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
