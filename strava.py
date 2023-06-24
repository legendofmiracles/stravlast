import pickle
import time
import requests
import os


def get_token(oauth_code=None):
    if not os.path.exists("refresh_token.p"):
        # first time running
        token_response = requests.post(
            "https://www.strava.com/api/v3/oauth/token",
            data={
                "client_id": os.environ.get("client_id"),
                "client_secret": os.environ.get("client_secret"),
                "code": oauth_code,
                "grant_type": "authorization_code",
            },
        ).json()
        print(token_response)

        token = token_response["access_token"]
        open("refresh_token.p", "wb").write(
            pickle.dumps(
                (token_response["refresh_token"], token_response["expires_at"], token)
            )
        )

        return token
    else:
        file = open("refresh_token.p", "rb+")
        refresh = pickle.load(file)

        if time.time() >= refresh[1]:
            # need to refresh
            token_response = requests.post(
                "https://www.strava.com/api/v3/oauth/token",
                data={
                    "client_id": os.environ.get("client_id"),
                    "client_secret": os.environ.get("client_secret"),
                    "refresh_token": refresh[0],
                    "grant_type": "refresh_token",
                },
            ).json()
            token = token_response["access_token"]
            file.write(
                pickle.dumps(
                    (
                        token_response["refresh_token"],
                        token_response["expires_at"],
                        token,
                    )
                )
            )
            file.close()
            return token
        else:
            return refresh[2]


# set oauth_code to the codeon first run
print(get_token())
