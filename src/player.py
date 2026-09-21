import threading
import time

from audio import *
from yt_download import *
from platter import *

# Song download statuses
FAILED = -1
UNKNOWN = 0
DOWNLOADED = 1

# Holds song info and their download statuses
songs = []
download_status = []

# Holds index of playing song, and player online status
last_played_index = 0
playing_index = 0
playlist_active = False

# Used to store pre-decoded song bytes
prev_decoded = None
curr_decoded = None
next_decoded = None

# Playlist setup, then starts song loop
def start_playlist(tracks):

    global songs
    global download_status
    global playing_index
    global playlist_active
    global last_played_index
    global prev_decoded
    global curr_decoded
    global next_decoded

    songs = tracks
    download_status = [UNKNOWN] * len(tracks)

    playing_index = 0
    playlist_active = True
    last_played_index = 0

    prev_decoded = None
    curr_decoded = None
    next_decoded = None

    # Starts a downloader thread to pre-download all songs in playlist
    download_thread = threading.Thread(
        target=download_worker,
        daemon=True
    )
    download_thread.start()

    # Enters music player loop
    song_loop()


# Repeatedly plays songs until the end of a playlist
def song_loop():

    global playing_index
    global playlist_active
    global last_played_index
    global prev_decoded
    global curr_decoded
    global next_decoded

    # If player is shut off manually, exit the song loop
    while playlist_active:

        # If song index goes past playlist length, end playlist
        current_index = playing_index
        if current_index >= len(songs):
            break

        # Wait for download or skip a failed download
        current_status = download_status[current_index]
        if current_status == UNKNOWN:
            time.sleep(0.05)
            continue
        if current_status == FAILED:
            playing_index += 1
            continue

        # Once song is found in cache, fetch past decode or decode manually
        else:
            start_motor()
            print(f"NOW PLAYING: [{songs[playing_index]["name"]}]")
            song_path = get_cached_path(songs[current_index])
            song_audio = None
            if curr_decoded is not None:
                song_audio = curr_decoded
            else:  
                song_audio = decode_song(song_path)

            # Start decoder threads for nearby songs, if applicable
            if current_index > 0 and prev_decoded is None:
                prev_thread = threading.Thread(
                    target=decode_prev,
                    args=(current_index - 1,),
                    daemon=True
                ) 
                prev_thread.start()
            if current_index < len(songs) - 1 and next_decoded is None:
                next_thread = threading.Thread(
                    target=decode_next,
                    args=(current_index + 1,),
                    daemon=True
                )
                next_thread.start()

            # Store song index and play chosen song
            last_played_index = playing_index
            play_song(song_audio)

            # If no rewind was called, move forward a song and preserve decoded audio
            if playing_index == current_index:
                playing_index += 1
                curr_decoded = next_decoded
                prev_decoded = song_audio
                next_decoded = None
            # If rewind was called, go back a song and preserve decoded audio
            else:
                curr_decoded = prev_decoded
                prev_decoded = None
                next_decoded = song_audio


    # Once last song ends, turn off playlist
    playlist_active = False
    stop_motor()
    print("Playlist finished")


# Helper function for decoder thread for previous song
def decode_prev(song_index):
    global prev_decoded

    # Wait until song is downloaded
    song_path = wait_for_download(song_index)
    if song_path is None:
        return
    
    # Decode song, and store it if correct song is still being played
    audio = decode_song(song_path)
    if playing_index - 1 == song_index:
        prev_decoded = audio


# Helper function for decoder thread
def decode_next(song_index):
    global next_decoded

    # Wait until song is downloaded
    song_path = wait_for_download(song_index)
    if song_path is None:
        return

    # Decode song, and store it if correct song is still being played
    audio = decode_song(song_path)
    if playing_index + 1 == song_index:
        next_decoded = audio


# Ran by song download thread to download all songs in the background
def download_worker():

    global download_status
    songs_found = 0

    # If playlist suddenly ends, return immediately
    while playlist_active:

        # Once all songs are downloaded, return
        if songs_found == len(songs):
            return

        # Downloads all undownloaded songs starting from current song and moving forward
        for song_index in range(0, len(songs)):
            download_index = (playing_index + song_index) % len(songs)

            # Skip any song that downloaded, failed to download, or is in cache
            if (download_status[download_index] != UNKNOWN):
                continue

            if get_cached_path(songs[download_index]) is not None:
                download_status[download_index] = DOWNLOADED
                songs_found += 1
                continue

            # If song hasn't been downloaded, attempt a download
            else:
                song_path = download_song(songs[download_index])
                if song_path is not None:
                    download_status[download_index] = DOWNLOADED
                    songs_found += 1
                else:
                    download_status[download_index] = FAILED
                    songs_found += 1


# Waits until a song has been downloaded, and returns its path
def wait_for_download(song_index):

    # If playlist ends, return immediately
    while playlist_active:

        # If download failed, return None
        if download_status[song_index] == FAILED:
            return None

        # If the song's path exists, the download succeeded, and return it
        song_path = get_cached_path(songs[song_index])
        if song_path is not None:
            return song_path

        time.sleep(0.05)


# Ends the playlist
def stop_playlist():

    global playlist_active
    playlist_active = False
    end_current_song()


# Skips to the next song, or end the playlist if last song
def skip():
    end_current_song()


# Goes to the previous song, if a previous song exists
def go_back():

    global playing_index

    if playing_index > 0:
        playing_index -= 1
        end_current_song()
