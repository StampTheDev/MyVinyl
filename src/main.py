from audio import *
from database import *
from nfc_reader import *

def main():

    while True:

        input("Press Enter to detect NFC...")
        nfc_id = detect_nfc()

        print(f"Detected NFC: {nfc_id}")
        input("Press Enter to look up song...")

        song_info = get_song_by_nfcid(nfc_id)

        if song_info is None:
            print(f"No song assigned to NFC tag {nfc_id}")
            continue

        print(f"Song info: {song_info}")
        input("Press Enter to download song...")

        local_path = download_song(song_info["filepath"])

        print(f"Downloaded to: {local_path}")
        input("Press Enter to play song...")

        play_song(local_path)
        print("Song ended...")

if __name__ == "__main__":
    main()