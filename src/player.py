import threading
import time

from audio import *
from yt_download import *
from platter import *

FAILED = -1
UNKNOWN = 0
DOWNLOADED = 1

songs = []
download_status = []

playing_index = 0
player_active = False

def start_playlist(tracks):

    global songs
    global download_status
    global playing_index
    global player_active

    songs = tracks
    download_status = [UNKNOWN] * len(tracks)

    playing_index = 0
    player_active = True

    download_thread = threading.Thread(
        target=download_worker,
        daemon=True
    )

    download_thread.start()

    song_loop()

def song_loop():

    global playing_index
    global player_active

    start_motor()

    while player_active:

        current_index = playing_index
        if current_index >= len(songs):
            break

        current_status = download_status[playing_index]
        if current_status == UNKNOWN:
            time.sleep(0.05)
            continue

        if current_status == FAILED:
            playing_index += 1
            continue

        else:
            song_path = get_cached_path(songs[current_index])
            print(f"Playing song {current_index}")
            play_song(song_path)

            if playing_index == current_index:
                playing_index += 1

    player_active = False
    stop_motor()
    print("Playlist commenced")

def download_worker():

    global download_status
    songs_checked = 0

    while player_active:

        if songs_checked == len(songs):
            print(f"Download worker finished")
            return

        for song_index in range(0, len(songs)):
            download_index = (playing_index + song_index) % len(songs)

            if (download_status[download_index] != UNKNOWN):
                continue

            if get_cached_path(songs[download_index]) is not None:
                print(f"Song {download_index} already exists in cache")
                download_status[download_index] = DOWNLOADED
                songs_checked += 1
                continue

            else:
                song_path = download_song(songs[download_index])
                if song_path is not None:
                    print(f"Song {download_index} downloaded successfully")
                    download_status[download_index] = DOWNLOADED
                    songs_checked += 1
                else:
                    print(f"Error while downloading song {download_index}")
                    download_status[download_index] = FAILED
                    songs_checked += 1


def stop_playlist():

    global player_active

    player_active = False
    stop_song()
