import os, json
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

url = "https://osu.ppy.sh/api/v2"
token_url = "https://osu.ppy.sh/oauth/token"
auth_base_url = "https://osu.ppy.sh/oauth/authorize"


client = BackendApplicationClient(client_id=client_id, scope=["public"])
osu = OAuth2Session(client=client)
token = osu.fetch_token(
    token_url=token_url, client_id=client_id, client_secret=client_secret
)


r = osu.request("GET", f"{url}/users/4394718")
print(r.content)


# NOTES ON WHAT TO PRESERVE FROM API CALLS:
# get user (/users/{user}/{mode}):
#   PKEY(id), avatar_url, country_code, username, monthly_playcounts{FILTER BY YEAR=2023}, replays_watched_counts{FILTER BY YEAR=2023}
# get user top scores (/users/{user}/scores/best?mode={mode}&limit=100):
#   PKEY(id), user_id, accuracy, created_at, pp, rank, beatmap{version}, beatmapset{artist, title, covers{list}}, maybe more here for aggregations
# get user beatmap scores (/beatmaps/{beatmap}/scores/users/{user}/all):
#   position, score{PKEY(id, best_id), user_id, accuracy, mods, score, max_combo, statistics.count_300, statistics.count_100, statistics.count_50, passed, pp, rank, created_at, mode}
