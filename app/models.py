from typing import Any, Dict, List
from app import db
from app.utils.enums import Mode, Status, Grade


class User(db.Model):
    """
    Contains data related to an osu! user.
    https://osu.ppy.sh/docs/index.html#user

    User data is returned for every valid request passing through the application:
        GET ".../users/{user}/{mode}"
    """

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    country_code = db.Column(db.String(2))
    avatar_url = db.Column(db.String(255))
    beatmaps_played_alltime = db.Column(db.Integer)
    achievements_2023 = db.Column(db.Integer, default=0)
    badges_2023 = db.Column(db.Integer, default=0)
    playcount_2023 = db.Column(db.Integer, default=0)
    replays_watched_2023 = db.Column(db.Integer, default=0)
    mode = db.Column(db.Enum(Mode), default="osu")

    def __init__(self, user: Dict[str, Any], mode: str) -> None:
        achievements_2023 = self.filter_by_2023(
            user["user_achievements"], "achievement_id", "achieved_at"
        )
        badges_2023 = self.filter_by_2023(user["badges"], "description", "awarded_at")
        playcount_2023 = self.filter_by_2023(
            user["monthly_playcounts"], "count", "start_date"
        )
        replays_2023 = self.filter_by_2023(
            user["replays_watched_counts"], "count", "start_date"
        )

        self.user_id = user["id"]
        self.username = user["username"]
        self.country_code = user["country_code"]
        self.avatar_url = user["avatar_url"]
        self.beatmaps_played_alltime = user["beatmap_playcounts_count"]
        self.achievements_2023 = len(achievements_2023)
        self.badges_2023 = len(badges_2023)
        self.playcount_2023 = sum(playcount_2023)
        self.replays_watched_2023 = sum(replays_2023)
        self.mode = Mode(mode)

    # def upsert(self) -> None:
    # record_exists = db.session.query(User).filter_by(user_id=self.user_id).first()

    # if record_exists:
    # record_exists.username = self.username
    # else:
    # db.session.add(self)

    # db.session.commit()

    def filter_by_2023(
        self, data: List[Dict[str, Any]], filter_by: str, date_key: str
    ) -> List[Any]:
        return [entry[filter_by] for entry in data if entry[date_key][:4] == "2023"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in [
                "user_id",
                "username",
                "country_code",
                "avatar_url",
                "beatmaps_played_alltime",
                "badges_2023",
                "playcount_2023",
                "replays_watched_2023",
                "mode",
            ]
        }


class Beatmap(db.Model):
    """
    Contains data related to an osu! beatmap, including details on the beatmap set.
    https://osu.ppy.sh/docs/index.html#beatmap

    Beatmap data is returned when score data is requested:
        - GET ".../users/{user}/scores/{type}"
    """

    __tablename__ = "Beatmaps"

    beatmap_id = db.Column(db.Integer, unique=True, primary_key=True)
    beatmapset_id = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    version = db.Column(db.String(128), nullable=False)
    creator = db.Column(db.String(32), nullable=False)
    play_count = db.Column(db.Integer)
    status = db.Column(db.Enum(Status))
    difficulty_rating = db.Column(db.Float)
    length = db.Column(db.Integer)
    bpm = db.Column(db.Float)
    approach_rate = db.Column(db.Float)
    circle_size = db.Column(db.Float)
    overall_difficulty = db.Column(db.Float)
    hp_drain = db.Column(db.Float)
    cover_url = db.Column(db.String(255))
    list_url = db.Column(db.String(255))
    mode = db.Column(db.Enum(Mode), default="osu")

    def __init__(self, play: Dict[str, Any], mode: str) -> None:
        map = play["beatmap"]
        set = play["beatmapset"]

        self.beatmap_id = map["id"]
        self.beatmapset_id = map["beatmapset_id"]
        self.artist = set["artist"]
        self.title = set["title"]
        self.version = map["version"]
        self.creator = set["creator"]
        self.play_count = map["playcount"]
        self.status = Status(map["status"])
        self.difficulty_rating = map["difficulty_rating"]
        self.length = map["hit_length"]
        self.bpm = map["bpm"]
        self.approach_rate = map["ar"]
        self.circle_size = map["cs"]
        self.overall_difficulty = map["accuracy"]
        self.hp_drain = map["drain"]
        self.cover_url = set["covers"]["cover"]
        self.list_url = set["covers"]["list"]
        self.mode = Mode(map["mode"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in [
                "beatmap_id",
                "beatmapset_id",
                "artist",
                "title",
                "version",
                "creator",
                "play_count",
                "status",
                "difficulty_rating",
                "length",
                "bpm",
                "approach_rate",
                "circle_size",
                "overall_difficulty",
                "hp_drain",
                "cover_url",
                "list_url",
                "mode",
            ]
        }


class Score(db.Model):
    """
    Contains data related to an osu! score.
    https://osu.ppy.sh/docs/index.html#score

    Score data is returned when collecting a user's best scores, or getting an individual score:
        - GET ".../users/{user}/scores/{type}"
        - GET ".../beatmaps/{beatmap}/scores/users/{user}/all"
    """

    __tablename__ = "Scores"

    score_id = db.Column(db.BigInteger, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    beatmap_id = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float)
    pp = db.Column(db.Float)
    mods = db.Column(db.String(32))
    score = db.Column(db.Integer)
    letter_grade = db.Column(db.Enum(Grade))
    max_combo = db.Column(db.Integer)
    count_300 = db.Column(db.Integer)
    count_100 = db.Column(db.Integer)
    count_50 = db.Column(db.Integer)
    count_miss = db.Column(db.Integer)
    passed = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    mode = db.Column(db.Enum(Mode), default="osu")

    def __init__(self, play: Dict[str, Any], mode: str) -> None:
        self.score_id = play["id"]
        self.user_id = play["user_id"]
        self.beatmap_id = play["beatmap"]["id"]
        self.accuracy = round(play["accuracy"], 4)
        self.mods = ",".join(play["mods"])
        self.pp = play["pp"]
        self.score = play["score"]
        self.letter_grade = Grade(play["rank"])
        self.max_combo = play["max_combo"]
        self.count_300 = play["statistics"]["count_300"]
        self.count_100 = play["statistics"]["count_100"]
        self.count_50 = play["statistics"]["count_50"]
        self.count_miss = play["statistics"]["count_miss"]
        self.passed = play["passed"]
        self.created_at = play["created_at"]
        self.mode = Mode(mode)

    def to_dict(self) -> Dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in [
                "score_id",
                "user_id",
                "beatmap_id",
                "accuracy",
                "mods",
                "pp",
                "score",
                "letter_grade",
                "max_combo",
                "count_300",
                "count_100",
                "count_50",
                "count_miss",
                "passed",
                "created_at",
                "mode",
            ]
        }


class BestScore(db.Model):
    """
    Contains data related to a user's best scores (also known as "top plays").
    The data stored here does not directly correspond to an object in the API.

    BestScore data is generated by the application when collecting a user's best scores:
        - GET ".../users/{user}/scores/{type}"
    """

    __tablename__ = "BestScores"
    best_score_sk = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    beatmap_id = db.Column(db.Integer, nullable=False)
    performance_rank = db.Column(db.Integer)

    def __init__(self, idx: int, play: Dict[str, Any], mode: str) -> None:
        self.score_id = play["id"]
        self.user_id = play["user_id"]
        self.beatmap_id = play["beatmap"]["id"]
        self.performance_rank = idx + 1
        self.mode = Mode(mode)

    def to_dict(self) -> Dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in ["score_id", "user_id", "beatmap_id", "performance_rank", "mode"]
        }
