from typing import Any, Dict
from app import db
from app.utils.enums import Mode, Status, Grade
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity
from enum import Enum


class User(db.Model):
    """
    data received from request to '/users/{user}/{mode}'
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

    def __init__(self, player, mode):
        badges_2023 = self.filter_badges(player["badges"])
        playcount_2023 = self.filter_playcount(player["monthly_playcounts"])
        replays_2023 = self.filter_replays(player["replays_watched_counts"])

        self.user_id = player["id"]
        self.user_name = player["username"]
        self.country_code = player["country_code"]
        self.avatar_url = player["avatar_url"]
        self.beatmaps_played_alltime = player["beatmap_playcounts_count"]
        self.badges_2023 = len(badges_2023)
        self.playcount_2023 = sum(playcount_2023)
        self.replays_watched_2023 = sum(replays_2023)
        self.mode = mode

    def filter_badges(badge_data):
        return [
            badge["awarded_at"]
            for badge in badge_data
            if badge["awarded_at"][:4] == "2023"
        ]

    def filter_playcount(playcount_data):
        return [
            playcount["count"]
            for playcount in playcount_data
            if playcount["start_date"][:4] == "2023"
        ]

    def filter_replays(replays_data):
        return [
            replay["count"]
            for replay in replays_data
            if replay["start_date"][:4] == "2023"
        ]


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
    length = db.Column(db.Integer)
    bpm = db.Column(db.Float)
    approach_rate = db.Column(db.Float)
    circle_size = db.Column(db.Float)
    overall_difficulty = db.Column(db.Float)
    hp_drain = db.Column(db.Float)
    cover_url = db.Column(db.String(255))
    list_url = db.Column(db.String(255))
    mode = db.Column(db.Enum(Mode), default="osu")

    def __init__(self, play, mode):
        map = play["beatmap"]
        set = play["beatmapset"]

        self.beatmap_id = map["id"]
        self.beatmapset_id = map["beatmapset_id"]
        self.artist = set["artist"]
        self.title = set["title"]
        self.version = map["version"]
        self.creator = set["creator"]
        self.play_count = map["playcount"]
        self.status = map["status"]
        self.difficulty_rating = map["difficulty_rating"]
        self.length = map["hit_length"]
        self.bpm = map["bpm"]
        self.approach_rate = map["ar"]
        self.circle_size = map["cs"]
        self.overall_difficulty = map["accuracy"]
        self.hp_drain = map["drain"]
        self.cover_url = set["covers"]["cover"]
        self.list_url = set["covers"]["list"]
        self.mode = map["mode"]


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

    def __init__(self, play, mode):
        self.score_id = play["id"]
        self.user_id = play["user_id"]
        self.beatmap_id = play["beatmap"]["id"]
        self.accuracy = round(play["accuracy"], 4)
        self.pp = play["pp"]
        self.mods = ",".join(play["mods"])
        self.score = play["score"]
        self.letter_grade = play["rank"]
        self.max_combo = play["max_combo"]
        self.count_300 = play["statistics"]["count_300"]
        self.count_100 = play["statistics"]["count_100"]
        self.count_50 = play["statistics"]["count_50"]
        self.count_miss = play["statistics"]["count_miss"]
        self.passed = play["passed"]
        self.created_at = play["created_at"]
        self.mode = mode


class BestScore(db.Model):
    """ """

    # __tablename__ = ...

    score_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, primary_key=True)
    beatmap_id = db.Column(db.Integer, unique=True, nullable=False)
    performance_rank = db.Column(db.Integer)

    def __init__(self, idx, play, mode):
        self.score_id = play["id"]
        self.user_id = play["user_id"]
        self.beatmap_id = play["beatmap"]["id"]
        self.performance_rank = idx + 1
        self.mode = mode
