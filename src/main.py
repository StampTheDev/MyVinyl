from audio import *
from database import *
from encoder import *
from nfc_reader import *
from platter import *
from player import *
from yt_download import *

def main():

    # Once a playlist ends, keep searching for the next record
    while True:

        # Read disk ID and retrieve songs
        nfc_id = detect_nfc()
        if nfc_id is None:
            continue
        print(f"Found NFC tag: {nfc_id}")

        tracks = retrieve_playlist(nfc_id)
        if not tracks:
            print("No songs found for this record")
            wait_for_record_removal(nfc_id)
            continue

        # Initialize thread to detect if record is removed
        monitor_stop = threading.Event()
        monitor_thread = threading.Thread(
            target=monitor_nfc,
            args=(nfc_id, stop_playlist, monitor_stop), daemon=True)
        monitor_thread.start()

        # Start playlist
        start_playlist(tracks)

        # Remove disk monitor once playlist ends
        monitor_stop.set()
        monitor_thread.join()

        # Once playlist ends, record must be removed before any disk will be read
        wait_for_record_removal(nfc_id)
        print(f"Waiting for next record")

if __name__ == "__main__":
     main()
