from stravalib import Client
import os

client = Client()
token_response = client.refresh_access_token(client_id=os.environ.get("client_id"),
                                      client_secret=os.environ.get("client_secret"),
                                      refresh_token=open("refresh_token", "r"))
f = open("refresh_token", "w")
f.write(token_response['refresh_token'])
f.close()


