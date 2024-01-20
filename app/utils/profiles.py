from typing import Any, Dict
from app.utils.osu import Osu
from app.utils.db import Dynamo


class ProfileDAO:
    def __init__(self) -> None:
        self.osu = Osu()
        self.db = Dynamo()

    def get_profile(self, user_input: str) -> Dict[str, Any]:
        user_profile = (
            self.db.get_profile_from_id(int(user_input))
            if user_input.isdigit()
            else self.db.get_profile_from_username(user_input)
        )

        if not user_profile:
            # User may not exist in the DB yet
            user_profile = self.process_new_user(user_input)

        return user_profile

    def process_new_user(self, user_input: str) -> Dict[str, Any]:
        user_profile = self.build_profile(user_input)

        if user_profile:
            user_profile_in_db = self.db.get_profile_from_id(user_profile["user_id"])
            # User may exist in DB under a different username than the one requested
            if user_profile_in_db:
                return user_profile_in_db

            self.db.insert_profile(user_profile)

        return user_profile

    def build_profile(self, user_input: str) -> Dict[str, Any]:
        user = self.osu.get_user(user_input)
        if user is None:
            return {}

        best_scores = self.osu.get_best_scores(user.user_id)

        return {
            **user.to_dict(),
            "best_scores_2023": [score.to_dict() for score in best_scores]
            if best_scores
            else [],
        }
