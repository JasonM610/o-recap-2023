import datetime
from typing import Any, Dict, List


class User:
    """
    Contains data related to an osu! user.
    https://osu.ppy.sh/docs/index.html#user

    User data is returned for every valid request passing through the application:
        GET ".../users/{user}"
    """

    user_id = int
    username = str
    country_code = str
    avatar_url = str
    beatmaps_played = int
    achievements_2023 = int
    badges_2023 = int
    playcount_2023 = int
    replays_watched_2023 = int

    def __init__(self, user: Dict[str, Any]) -> None:
        achieves = self.filter(user["user_achievements"], "achieved_at", "achieved_at")
        badges = self.filter(user["badges"], "description", "awarded_at")
        playcount = self.filter(user["monthly_playcounts"], "count", "start_date")
        replays = self.filter(user["replays_watched_counts"], "count", "start_date")

        self.user_id = user["id"]
        self.username = user["username"]
        self.country_code = user["country_code"]
        self.avatar_url = user["avatar_url"]
        self.beatmaps_played = user["beatmap_playcounts_count"]
        self.achievements_2023 = len(achieves)
        self.badges_2023 = len(badges)
        self.playcount_2023 = sum(playcount)
        self.replays_watched_2023 = sum(replays)

    def filter(self, data: List[Dict[str, Any]], agg_by: str, date: str) -> List[Any]:
        return [entry[agg_by] for entry in data if entry[date][:4] == "2023"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "country_code": self.country_code,
            "avatar_url": self.avatar_url,
            "beatmaps_played": self.beatmaps_played,
            "achievements_2023": self.achievements_2023,
            "badges_2023": self.badges_2023,
            "playcount_2023": self.playcount_2023,
            "replays_watched_2023": self.replays_watched_2023,
        }


class Score:
    """
    Contains data related to an osu! score.
    https://osu.ppy.sh/docs/index.html#score

    Score data is returned when collecting a user's best scores, or getting an individual score:
        - GET ".../users/{user}/scores/{type}"
        - GET ".../beatmaps/{beatmap}/scores/users/{user}/all"
    """

    score_id = int
    user_id = int
    beatmap_id = int
    accuracy = float
    pp = float
    mods = List[str]
    score = int
    letter_grade = str
    max_combo = int
    count_300 = int
    count_100 = int
    count_50 = int
    count_miss = int
    created_at = datetime

    def __init__(self, play: Dict[str, Any], beatmap_id: int) -> None:
        self.score_id = play["id"]
        self.user_id = play["user_id"]
        self.beatmap_id = beatmap_id
        self.accuracy = round(play["accuracy"], 4)
        self.mods = play["mods"] if len(play["mods"]) > 1 else ["NM"]
        self.pp = play["pp"]
        self.score = play["score"]
        self.letter_grade = play["rank"]
        self.max_combo = play["max_combo"]
        self.count_300 = play["statistics"]["count_300"]
        self.count_100 = play["statistics"]["count_100"]
        self.count_50 = play["statistics"]["count_50"]
        self.count_miss = play["statistics"]["count_miss"]
        self.created_at = play["created_at"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score_id": self.score_id,
            "user_id": self.user_id,
            "beatmap_id": self.beatmap_id,
            "mods": self.mods,
            "accuracy": str(self.accuracy),
            "pp": str(self.pp),
            "score": self.score,
            "letter_grade": self.letter_grade,
            "max_combo": self.max_combo,
            "count_300": self.count_300,
            "count_100": self.count_100,
            "count_50": self.count_50,
            "count_miss": self.count_miss,
            "created_at": self.created_at,
        }


class BestScore:
    """
    Contains data related to a user's best scores (also known as "top plays").
    The data stored here does not directly correspond to an object in the API.

    BestScore data is generated by the application when collecting a user's best scores:
        - GET ".../users/{user}/scores/{type}"
    """

    score_id = int
    user_id = int
    beatmap_id = int
    performance_rank = int
    mods = List[str]
    accuracy = float
    pp = float
    letter_grade = str
    artist = str
    title = str
    version = str
    creator_id = int
    cover_url = str
    list_url = str
    created_at = datetime

    def __init__(self, idx: int, play: Dict[str, Any]) -> None:
        map = play["beatmap"]
        set = play["beatmapset"]

        self.score_id = play["id"]
        self.user_id = play["user_id"]
        self.beatmap_id = play["beatmap"]["id"]
        self.performance_rank = idx + 1
        self.mods = play["mods"]
        self.accuracy = round(play["accuracy"], 4)
        self.pp = play["pp"]
        self.letter_grade = play["rank"]
        self.artist = set["artist"]
        self.title = set["title"]
        self.version = map["version"]
        self.creator_id = set["user_id"]
        self.cover_url = set["covers"]["cover"]
        self.list_url = set["covers"]["list"]
        self.created_at = play["created_at"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score_id": self.score_id,
            "user_id": self.user_id,
            "beatmap_id": self.beatmap_id,
            "performance_rank": self.performance_rank,
            "mods": self.mods,
            "accuracy": str(self.accuracy),
            "pp": str(self.pp),
            "letter_grade": self.letter_grade,
            "artist": self.artist,
            "title": self.title,
            "version": self.version,
            "creator_id": self.creator_id,
            "cover_url": self.cover_url,
            "list_url": self.list_url,
            "created_at": self.created_at,
        }
