from datetime import datetime, timedelta
from dateutil.parser import parse
import requests
import strava
import os

token = strava.get_token()


def mk_description(activity):
    laps = requests.get(
        f'https://www.strava.com/api/v3/activities/{activity["id"]}/laps',
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    end_time = parse(activity["start_date"]) + timedelta(
        seconds=int(activity["elapsed_time"])
    )

    all_songs = requests.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "user.getrecenttracks",
            "user": "mlomm",
            "to": end_time.timestamp(),
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
        i = i["distance"] / 1000
        distances.append(i)

    distances.reverse()
    distances.append(0)

    total_distance = sum(distances)
    for i in laps:
        songs = all_songs.copy()
        deleted = 0
        lap_desc = ""
        for s in range(len(songs)):
            song_time = int(songs[0]["date"]["uts"])
            lap_time = datetime.timestamp(parse(i["start_date"]))
            if song_time >= lap_time and not song_time > end_time.timestamp():
                lap_desc = (
                    lap_desc
                    + "\U0001F3B5 "
                    + songs[0]["name"]
                    + "  -  "
                    + songs[0]["artist"]["#text"]
                    + "\n"
                )
                del all_songs[s - deleted]
                deleted = deleted + 1

            del songs[0]
        total_distance = total_distance - distances[-1]
        del distances[-1]
        if deleted != 0:
            description = (
                f"\n{total_distance-distances[-1]}-{total_distance:.1f}. kilometer\n".replace(
                    ".0", ""
                )
                + lap_desc
                + description
            )

    description = description.lstrip()

    return description


# activity = list(client.get_activities(limit=1))[0]
activity = requests.get(
    "https://www.strava.com/api/v3/athlete/activities",
    headers={"Authorization": f"Bearer {token}"},
    params={"per_page": "1"},
).json()[0]

description = mk_description(activity)

if description != "":
    print(description)
    requests.put(
        f'https://www.strava.com/api/v3/activities/{activity["id"]}',
        headers={"Authorization": f"Bearer {token}"},
        data={"description": description},
    )
