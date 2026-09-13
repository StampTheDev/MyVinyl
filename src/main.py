from audio import *
from database import *
from encoder import *
from nfc_reader import *

def main():

    print("Starting mpv")
    start_mpv()
    print("MPV fully started")

    try:

        while True:

            nfc_id = None
            while nfc_id == None:
                nfc_id = detect_nfc()

            print(f"Detected NFC: {nfc_id}")

            song_info = get_song_by_nfcid(nfc_id)
            if song_info is None:
                print("No song assigned to record")
                continue

            print(f'Track Name: [{song_info["name"]}]')

            local_path = download_song(song_info["filepath"])

            print("Playing song...")
            play_song(local_path)
            song_finished.wait()
            print("Song finished")

    finally:

        stop_mpv()


if __name__ == "__main__":
     main()
