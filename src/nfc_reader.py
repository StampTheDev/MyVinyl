import board
import busio
import time
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)

pn532 = PN532_SPI(
    spi,
    cs_pin,
    debug=False
)
pn532.SAM_configuration()

def detect_nfc():

    uid = pn532.read_passive_target(timeout=0.1)

    if uid is None:
        return None

    uid_string = ""
    for byte in uid:
        uid_string += f"{byte:02X}"

    return uid_string


def monitor_nfc(record_id, on_removed, stop_event):

    blank_reads = 0

    print("NFC Monitor started")

    while not stop_event.is_set():

        nfc_id = detect_nfc()
        if nfc_id == record_id:
            blank_reads = 0
            print("Reading same record")
        else:
            print("Read blank")
            blank_reads += 1
        if blank_reads >= 2:
            print("Record removed")
            on_removed()
            return


# Also works for swapping the records
def wait_for_record_removal(record_id):

    blank_reads = 0

    while True:
        nfc_id = detect_nfc()
        if nfc_id == record_id:
            blank_reads = 0
        else:
            blank_reads += 1
        if blank_reads >= 2:
            return

        time.sleep(0.1)


if __name__ == "__main__":
    print("Waiting for NFC tag...")

    while True:
        tag_id = detect_nfc()
        if tag_id is not None:
            print("Identified tag w/ ID:", tag_id)
