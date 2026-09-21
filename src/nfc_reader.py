import board
import busio
import time
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

# Sets up SPI communication with NFC reader
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

# Registers reader as active device
cs_pin = DigitalInOut(board.D5)

# Creates and configures PN532 NFC reader object
pn532 = PN532_SPI(
    spi,
    cs_pin,
    debug=False
)
pn532.SAM_configuration()

# Attempts to find NFC tag within 0.1 second window
def detect_nfc():

    # Wait up to 0.1 seconds to read NFC tag ID, or none if none is found
    uid = pn532.read_passive_target(timeout=0.1)
    if uid is None:
        return None

    # Returns valid NFC id into readable string
    uid_string = ""
    for byte in uid:
        uid_string += f"{byte:02X}"
    return uid_string


# Watches for record removal and stops music if detected
def monitor_nfc(record_id, on_removed, stop_event):

    # Number of consecutive reads without detecting the target ID
    blank_reads = 0

    # While not stopped, attempt to read NFC id repeatedly
    while not stop_event.is_set():

        nfc_id = detect_nfc()

        # If two consecutive reads miss the expected NFC tag, disable the player
        if nfc_id == record_id:
            blank_reads = 0
        else:
            blank_reads += 1
        if blank_reads >= 2:
            print("Record removed")
            on_removed()
            return


# Holds the program until the record is removed
def wait_for_record_removal(record_id):

    # Number of consecutive reads without detecting the target id
    blank_reads = 0

    while True:
        nfc_id = detect_nfc()

        # If two consecutive reads miss the expected NFC tag, exit the wait
        if nfc_id == record_id:
            blank_reads = 0
        else:
            blank_reads += 1
        if blank_reads >= 2:
            return


if __name__ == "__main__":
    print("Waiting for NFC tag...")

    while True:
        tag_id = detect_nfc()
        if tag_id is not None:
            print("Identified tag w/ ID:", tag_id)
