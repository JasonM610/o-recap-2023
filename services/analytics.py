import polars as pl
import s3fs
from typing import Any, Dict
from app.utils.osu import Osu
from services.utils.scores import build_scores_df
from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_SCORE_BUCKET


class Analytics:
    osu = Osu()

    def __init__(self, user: Dict[str, Any]) -> None:
        self.user_id = user["user_id"]
        self.scores = build_scores_df(user["user_id"], user["beatmaps_played"])

    def get_analytics(self) -> Dict[str, Any]:
        return (
            {
                "year_pp": self.get_2023_pp(),
                "highest_sr_pass": self.get_highest_sr_pass(),
                "avg": self.get_averages(),
                "agg": self.get_aggregates(),
            }
            if not self.scores.is_empty()
            else {}
        )

    def get_2023_pp(self) -> str:
        # filter self.scores list to ranked maps, get highest pp score on each map
        best_scores = (
            self.scores.filter(pl.col("ranked") == 1)
            .group_by("beatmap_id")
            .agg(pl.col("pp").max())
        )

        # assign rank to each score based on pp value, return weighted sum
        score_ranking = best_scores["pp"].rank(method="ordinal", descending=True)
        return str(round((best_scores["pp"] * (0.95 ** (score_ranking - 1))).sum(), 3))

    def get_highest_sr_pass(self) -> Dict[str, Any]:
        passes = self.scores.filter(~pl.col("mods").str.contains("NF")).filter(
            pl.col("ranked") == 1
        )

        if passes.is_empty():
            return {}

        best_pass = passes[passes["star_rating"].arg_max()]
        beatmap_id = best_pass["beatmap_id"][0]
        beatmap_data = self.osu.get_beatmap(beatmap_id)

        return {
            "beatmap_id": best_pass["beatmap_id"][0],
            "artist": beatmap_data["beatmapset"]["artist"],
            "title": beatmap_data["beatmapset"]["title"],
            "version": beatmap_data["version"],
            "mods": best_pass["mods"][0],
            "acc": str(round(best_pass["accuracy"][0], 4)),
            "pp": round(best_pass["pp"][0]),
            "letter_grade": best_pass["letter_grade"][0],
            "combo": best_pass["max_combo"][0],
            "max_combo": beatmap_data["max_combo"],
            "sr": str(round(best_pass["star_rating"][0], 2)),
            "background_url": beatmap_data["beatmapset"]["covers"]["card@2x"],
        }

    def get_averages(self) -> Dict[str, Any]:
        return {
            "ar": str(round(self.scores["ar"].mean(), 2)),
            "cs": str(round(self.scores["cs"].mean(), 1)),
            "bpm": str(int(self.scores["bpm"].mean())),
            "acc": str(round(self.scores["accuracy"].mean(), 4)),
            "len": str(int(self.scores["length"].mean())),
            "sr": str(round(self.scores["star_rating"].mean(), 2)),
        }

    def get_aggregates(self) -> Dict[str, Any]:
        grade_counts = [
            self.scores.filter(pl.col("letter_grade") == grade)
            .select(pl.count())
            .item()
            for grade in ["XH", "SH", "X", "S", "A", "B", "C", "D"]
        ]

        map_counts = self.scores["set_owner"].value_counts(sort=True).head(3)
        map_counts = map_counts.with_columns(
            map_counts["set_owner"]
            .apply(self.osu.get_user)
            .apply(
                lambda user: user.username
                if user is not None
                else map_counts["set_owner"]
            )
            .alias("username")
        )

        mod_counts = self.scores["mods"].value_counts(sort=True).head(3)

        map_counts = map_counts.rename({"count": "counts"})
        mod_counts = mod_counts.rename({"count": "counts"})

        return {
            "scores": self.scores.select(pl.count()).item(),
            "ranked_score": self.scores["score"].sum(),
            "letter_grades": grade_counts,
            "most_played_mappers": map_counts.to_dict(as_series=False),
            "most_played_mods": mod_counts.to_dict(as_series=False),
        }

    def write_scores(self) -> None:
        if self.scores.is_empty():
            return

        s3 = s3fs.S3FileSystem(key=AWS_ACCESS_KEY, secret=AWS_SECRET_ACCESS_KEY)
        with s3.open(f"{AWS_SCORE_BUCKET}/scores/{self.user_id}.csv", "wb") as f:
            self.scores.write_csv(f, separator=",")
