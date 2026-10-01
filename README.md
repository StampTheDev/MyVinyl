# MyVinyl

MyVinyl is a programmable record player prototype built with a Raspberry Pi.

Each physical record contains an NFC tag that identifies a digital playlist. Placing a record on the player loads its playlist, starts playback, and spins the platter. The player uses physical controls for playback so, after being programmed, music can be controlled without using a phone or computer.

## Hardware

MyVinyl currently uses:

- Raspberry Pi 4
- PN532 NFC reader
- NFC tags
- MAX98357A I²S audio amplifier
- Speaker
- DC motor
- DRV8833 motor driver
- Two rotary encoders

## Controls

### Records

- **Place a record:** Load its assigned playlist and begin playback
- **Remove a record:** Stop playback

### Left Encoder

- **Rotate:** Adjust volume
- **Press:** Go back to previous song

### Right Encoder

- **Rotate:** Rewind or fast-forward through the current song
- **Press:** Skip to the next song

### Both Encoders

- **Press:** Pause/Unpause

## Setup

MyVinyl is designed to run on Raspberry Pi OS. Install the OS and connect to the Pi

### 1. Clone the Repository

```bash
git clone https://github.com/StampTheDev/MyVinyl.git
cd MyVinyl
```

### 2. Run the Setup Script

Make the setup script executable:

```bash
chmod +x setup.sh
```

Run it:

```bash
./setup.sh
```

The setup script installs the required system and Python dependencies and configures SPI and I²S audio.

### 3. Configure Supabase

Create a `.env` file in the project directory:

```bash
nano .env
```

Add the required Supabase credentials:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

The `.env` file is excluded from Git.

### 4. Reboot

```bash
sudo reboot
```

### 5. Run MyVinyl

After the Raspberry Pi restarts:

```bash
cd ~/MyVinyl
source .venv/bin/activate
python src/main.py
```

MyVinyl will wait for a recognized NFC record to be placed on the player.

Press `Ctrl+C` to stop the program.

## Optional: Run MyVinyl Automatically at Boot

MyVinyl can be configured to start automatically when the Raspberry Pi powers on, allowing it to operate without a laptop or terminal connection.

### 6. Create a systemd service

Create the service file:

```bash
sudo nano /etc/systemd/system/MyVinyl.service
```

Add:

```ini
[Unit]
Description=MyVinyl Record Player
Wants=network-online.target
After=network-online.target sound.target

[Service]
Type=simple
User=stamp
WorkingDirectory=/home/stamp/MyVinyl
ExecStart=/home/stamp/MyVinyl/.venv/bin/python /home/stamp/MyVinyl/src/main.py

Environment=PYTHONUNBUFFERED=1

Restart=on-failure
RestartSec=5

KillSignal=SIGINT
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
```

If your Raspberry Pi username or project directory is different, update `User`, `WorkingDirectory`, and `ExecStart` accordingly.

### 7. Enable the service

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable MyVinyl at startup:

```bash
sudo systemctl enable MyVinyl
```

Start it immediately:

```bash
sudo systemctl start MyVinyl
```

### 8. Check the service

Check whether MyVinyl is running:

```bash
systemctl status MyVinyl
```

View live program output:

```bash
journalctl -u MyVinyl -f
```

Pressing `Ctrl+C` while viewing the journal only exits the log viewer. MyVinyl will continue running in the background.

### Managing MyVinyl

```bash
sudo systemctl start MyVinyl
sudo systemctl stop MyVinyl
sudo systemctl restart MyVinyl
```

Once enabled, MyVinyl will automatically start whenever the Raspberry Pi boots and wait for an NFC record to be placed on the player, so long as the Pi is powered on and has internet access
