from audio import *
from database import *
from nfc_reader import *

def main():

    while True:

        nfc_id = None

        while nfc_id is None:
            nfc_id = detect_nfc()

        print(f"Detected NFC: {nfc_id}")

        song_info = get_song_by_nfcid(nfc_id)

        if song_info is None:
            print(f"No song assigned to NFC tag {nfc_id}")
            continue

        print(f"Song info: {song_info}")

        local_path = download_song(song_info["filepath"])
        play_song(local_path)

if __name__ == "__main__":
    main()
