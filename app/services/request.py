import os, json
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

api_base_url = "https://osu.ppy.sh/api/v2"
token_url = "https://osu.ppy.sh/oauth/token"


client = BackendApplicationClient(client_id=client_id, scope=["public"])
session = OAuth2Session(client=client)
token = session.fetch_token(
    token_url=token_url, client_id=client_id, client_secret=client_secret
)


def send_request(url: str) -> None:
    return session.request("GET", f"{api_base_url}{url}")


r = send_request("/users/12408961/osu")
print(r.content)

# temp = json.dumps(r.json(), indent=4)
# with open("test_3.json", "w") as outfile:
# outfile.write(temp)
