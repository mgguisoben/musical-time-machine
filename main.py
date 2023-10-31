import datetime
import os

import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_ID = os.environ.get("SPOTIFY_ID")
SPOTIFY_SECRET = os.environ.get("SPOTIFY_SECRET")

print("Which year do you want to travel to?")
birth_date = ""

date_format_correct = False
while not date_format_correct:
    try:
        birth_date = input("Type the date in this format (YYYY-MM-DD): ")
        check_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
        date_format_correct = True

    except ValueError:
        print("Please follow the date format.")

# Web scraping Billboard for song info
billboard_endpoint = f"https://www.billboard.com/charts/hot-100/{birth_date}"
response = requests.get(url=billboard_endpoint).text

soup = BeautifulSoup(response, "html.parser")
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]
song_artists_spans = soup.select("li ul li span")
song_artists = [song.getText().strip() for song in song_artists_spans[::7]]

songs = zip(song_names, song_artists)
year = birth_date.split("-")[0]
song_uris = []

# Authenticate access through spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_ID,
                                               client_secret=SPOTIFY_SECRET,
                                               redirect_uri="https://example.org/callback",
                                               scope="playlist-modify-public",
                                               show_dialog=True,
                                               cache_path="token.txt"
                                               )
                     )

# Get Spotify user ID
user_id = sp.current_user()["id"]

# Get song uri's
for song in songs:
    result = sp.search(q=f"track:{song[0]} artist:{song[1]} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Add songs to playlist
playlist = sp.user_playlist_create(user=user_id, name=f"Billboard Hot 100 on {birth_date}", public=True)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

print("Done!")
