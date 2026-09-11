import board
import busio
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
    uid = pn532.read_passive_target(timeout=0.5)

    if uid is None:
        return None

    uid_string = ""
    for byte in uid:
        uid_string += f"{byte:02X}"

    return uid_string

if __name__ == "__main__":
    print("Waiting for NFC tag...")

    while True:
        tag_id = detect_nfc()
        if tag_id is not None:
            print("Identified tag w/ ID:", tag_id)
