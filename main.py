from stravalib import Client
import os
from datetime import datetime
import requests

client = Client()

# ONLY DO THIS THE FIRST TIME
# url = client.authorization_url(client_id=os.environ.get("client_id"),
#                               redirect_uri='http://127.0.0.1:5000/authorization',
#                               scope = ["activity:read_all", "activity:write"])

# token_response = client.exchange_code_for_token(client_id=os.environ.get("client_id"),
#                                              client_secret=os.environ.get("client_secret"),
#                                              code="00dc91540844d8d619708acaef42ddc2db9c58e5")

token_response = client.refresh_access_token(
    client_id=os.environ.get("client_id"),
    client_secret=os.environ.get("client_secret"),
    refresh_token=open("refresh_token", "r"),
)

client = Client(access_token=token_response["access_token"])

f = open("refresh_token", "w")
f.write(token_response["refresh_token"])
f.close()


activity = list(client.get_activities(limit=1))[0]
laps = client.get_activity_laps(activity.id)

end_time = (
    datetime.timestamp(activity.start_date) + activity.elapsed_time.total_seconds()
)

all_songs = requests.get(
    "http://ws.audioscrobbler.com/2.0/",
    params={
        "method": "user.getrecenttracks",
        "user": "mlomm",
        "to": int(end_time),
        "api_key": os.environ.get("last_key"),
        "format": "json",
    },
).json()["recenttracks"]["track"]

# last.fm always includes the currently playing song in the list
if "@attr" in all_songs[0] and "nowplaying" in all_songs[0]["@attr"]:
    del all_songs[0]

description = ""

laps = list(laps)
laps.reverse()
all_songs.reverse()


for i in laps:
    songs = all_songs.copy()
    deleted = 0
    for s in range(len(songs)):
        song_time = int(songs[0]["date"]["uts"])
        lap_time = datetime.timestamp(i.start_date)
        # print(song_time)
        # print(lap_time)
        # print("\n")
        if song_time >= lap_time:
            description = songs[0]["name"] + "\n" + description
            del all_songs[s - deleted]
            deleted = deleted + 1

        del songs[0]
    description = "kilometer " + str(i.distance) + "\n" + description

print(description)
