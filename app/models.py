from app import db
from app.utils.enums import Mode, Status, Grade
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity
from enum import Enum


class User(db.Model):
    """
    data received from request to '/users/{user}/{mode}'
    table needs to support SCD1 since users may change their usernames between requests
    https://osu.ppy.sh/docs/index.html#user
    """

    # __tablename__ = ...
    user_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_name = db.Column(db.String(32), nullable=False)
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
    artist = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    version = db.Column(db.String(128), nullable=False)
    creator = db.Column(db.String(32), nullable=False)
    play_count = db.Column(db.Integer)
    status = db.Column(db.Enum(Status))
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


class Score(db.Model):
    """ """

    # __tablename__ = ...
    score_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    beatmap_id = db.Column(db.Integer, unique=True, nullable=False)
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


class UserBestPerformance(db.Model):
    """ """

    # __tablename__ = ...

    score_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, primary_key=True)
    beatmap_id = db.Column(db.Integer, unique=True, nullable=False)
    performance_rank = db.Column(db.Integer)
