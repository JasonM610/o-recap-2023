import os
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
