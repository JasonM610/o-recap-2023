from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity
from app import db

# need to add something about game mode to all


class User(db.Model):
    """
    data received from request to '/users/{user}/{mode}'
    https://osu.ppy.sh/docs/index.html#user
    """

    # __tablename__ = ...
    user_key = db.Column(db.Integer, Identity(), primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    user_name = db.Column(db.String(40), nullable=False)
    country_code = db.Column(db.String(2))
    avatar_url = db.Column(db.String(255))
    num_badges = db.Column(db.Integer, default=0)
    yearly_playcount = db.Column(db.Integer, default=0)
    yearly_replays_watched = db.Column(db.Integer, default=0)


class BeatmapScore(db.Model):
    """ """

    # __tablename__ = ...
    score_key = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    beatmap_id = db.Column(db.Integer, unique=True, nullable=False)
    score_id = db.Column(db.Integer, unique=True, nullable=False)
    accuracy = db.Column(db.Float)
    pp = db.Column(db.Float)
    mods = db.Column(db.String(40))
    score = db.Column(db.Integer)
    leaderboard_rank = db.Column(db.Integer)
    max_combo = db.Column(db.Integer)
    count_300 = db.Column(db.Integer)
    count_100 = db.Column(db.Integer)
    count_50 = db.Column(db.Integer)
    count_miss = db.Column(db.Integer)
    passed = db.Column(db.Boolean)
    letter_grade = db.Column(db.String(2))
    created_at = db.Column(db.DateTime)
    mode_int = db.Column(db.SmallInteger)


class UserBestPerformance(db.Model):
    """
    Data received from request to '/users/{user}/scores/best?limit=100&mode={mode}'
    https://osu.ppy.sh/docs/index.html#get-user-scores
    https://osu.ppy.sh/docs/index.html#score
    """

    # __tablename__ = ...
    score_key = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    beatmap_id = db.Column(db.Integer, unique=True, nulllable=False)
    score_id = db.Column(db.Integer, unique=True, nullable=False)
    accuracy = db.Column(db.Float)
    pp = db.Column(db.Float)
    mods = db.Column(db.String(40))
    score = db.Column(db.Integer)
    best_performance_rank = db.Column(db.Integer)
    letter_grade = db.Column(db.String(2))
    created_at = db.Column(db.DateTime)
    mode_int = db.Column(db.SmallInteger)


# NOTES ON WHAT TO PRESERVE FROM API CALLS:
# get user (/users/{user}/{mode}):
#   id, avatar_url, country_code, username, monthly_playcounts, replays_watched_counts, badges
# get user top scores (/users/{user}/scores/best?mode={mode}&limit=100):
#   id, user_id, accuracy, created_at, pp, rank, beatmap{version}, beatmapset{artist, title, covers{list}}, maybe more here for aggregations
# get user beatmap scores (/beatmaps/{beatmap}/scores/users/{user}/all):
#   position, score{id, best_id, user_id, accuracy, mods, score, max_combo, statistics.count_300, statistics.count_100, statistics.count_50, passed, pp, rank, created_at, mode}
