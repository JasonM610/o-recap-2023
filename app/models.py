from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity
from app import db


# move this to another file w/ datetime help
class Mode(Enum):
    osu = "osu"
    taiko = "taiko"
    ctb = "fruits"
    mania = "mania"


class User(db.Model):
    """
    data received from request to '/users/{user}/{mode}'
    table needs to support SCD1 since users may change their usernames between requests
    https://osu.ppy.sh/docs/index.html#user
    """

    # __tablename__ = ...
    user_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_name = db.Column(db.String(40), nullable=False)
    country_code = db.Column(db.String(2))
    avatar_url = db.Column(db.String(255))
    beatmaps_played_alltime = db.Column(db.Integer)
    badges_2023 = db.Column(db.Integer, default=0)
    playcount_2023 = db.Column(db.Integer, default=0)
    replays_watched_2023 = db.Column(db.Integer, default=0)
    mode = db.Column(db.Enum(Mode), default="osu")


class Beatmap(db.Model):
    """ """

    # __tablename__ = ...
    beatmap_id = db.Column(db.Integer, unique=True, primary_key=True)
    beatmapset_id = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    creator = db.Column(db.String(40), nullable=False)
    play_count = db.Column(db.Integer)
    status = db.Column(db.Enum(Status), default="???")  # figure this out
    difficulty_rating = db.Column(db.Float)
    total_length = db.Column(db.Integer)
    bpm = db.Column(db.Float)
    approach_rate = db.Column(db.Float)
    circle_size = db.Column(db.Float)
    overall_difficulty = db.Column(db.Float)
    hp_drain = db.Column(db.Float)
    cover_url = db.Column(db.String(255))
    list_url = db.Column(db.String(255))
    mode = db.Column(db.Enum(Mode), default="osu")


class BeatmapScore(db.Model):
    """ """

    # __tablename__ = ...
    score_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    beatmap_id = db.Column(db.Integer, unique=True, nullable=False)
    accuracy = db.Column(db.Float)
    pp = db.Column(db.Float)
    mods = db.Column(db.String(40))
    leaderboard_rank = db.Column(db.Integer)
    score = db.Column(db.Integer)
    letter_grade = db.Column(db.String(2))
    max_combo = db.Column(db.Integer)
    count_300 = db.Column(db.Integer)
    count_100 = db.Column(db.Integer)
    count_50 = db.Column(db.Integer)
    count_miss = db.Column(db.Integer)
    passed = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
    mode = db.Column(db.Enum(Mode), default="osu")


class UserBestScore(db.Model):
    """
    Data received from request to '/users/{user}/scores/best?limit=100&mode={mode}'
    https://osu.ppy.sh/docs/index.html#get-user-scores
    https://osu.ppy.sh/docs/index.html#score
    """

    # __tablename__ = ...
    score_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    beatmap_id = db.Column(db.Integer, unique=True, nullable=False)
    accuracy = db.Column(db.Float)
    pp = db.Column(db.Float)
    mods = db.Column(db.String(40))
    rank = db.Column(db.Integer)
    score = db.Column(db.Integer)
    letter_grade = db.Column(db.String(2))
    date = db.Column(db.DateTime)
    mode = db.Column(db.Enum(Mode), default="osu")


# NOTES ON WHAT TO PRESERVE FROM API CALLS:
# get user (/users/{user}/{mode}):
#   id, avatar_url, country_code, username, monthly_playcounts, replays_watched_counts, badges
# get user top scores (/users/{user}/scores/best?mode={mode}&limit=100):
#   id, user_id, accuracy, created_at, pp, rank, beatmap{version}, beatmapset{artist, title, covers{list}}, maybe more here for aggregations
# get user beatmap scores (/beatmaps/{beatmap}/scores/users/{user}/all):
#   position, score{id, best_id, user_id, accuracy, mods, score, max_combo, statistics.count_300, statistics.count_100, statistics.count_50, passed, pp, rank, created_at, mode}
