from datetime import datetime
import requests
from pint import UnitRegistry
import strava

ureg = UnitRegistry()

token = strava.get_token()

# activity = list(client.get_activities(limit=1))[0]
activity = requests.get(
    "https://www.strava.com/api/v3/athlete/activities",
    headers={"Authorization": f"Bearer {token}"},
    params={"per_page": "1"},
).json()[0]

print(activity)

laps = requests.get(
    f'https://www.strava.com/api/v3/activities/{activity["id"]}/laps',
    headers={"Authorization": f"Bearer {token}"},
).json()

end_time = datetime.fromisoformat(activity["start_date"]) + int(
    activity["elapsed_time"]
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

laps.reverse()
all_songs.reverse()

distances = []
for i in laps:
    i = i.distance.to(ureg.kilometer)
    distances.append(float(f"{i:~P}".replace(" km", "")))

distances.reverse()
distances.append(0)

total_distance = sum(distances)
for i in laps:
    songs = all_songs.copy()
    deleted = 0
    for s in range(len(songs)):
        song_time = int(songs[0]["date"]["uts"])
        lap_time = datetime.timestamp(i.start_date)
        if song_time >= lap_time:
            description = (
                "\U0001F3B5 "
                + songs[0]["name"]
                + "  -  "
                + songs[0]["artist"]["#text"]
                + "\n"
                + description
            )
            del all_songs[s - deleted]
            deleted = +1

        del songs[0]
    total_distance = total_distance - distances[-1]
    del distances[-1]
    if deleted != 0:
        description = (
            f"\n{total_distance-distances[-1]}-{total_distance:.1f}. kilometer\n".replace(
                ".0", ""
            )
            + description
        )

description = description.lstrip()

print(description)

client.update_activity(activity, description)
