#!/bin/bash

set -e

echo "Setting up MyVinyl..."

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y \
    ffmpeg \
    libportaudio2 \
    liblgpio-dev \
    swig \
    python3-venv

echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

echo "Installing Python dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Enabling SPI..."
sudo raspi-config nonint do_spi 0

CONFIG="/boot/firmware/config.txt"

if ! grep -q "^dtparam=i2s=on" "$CONFIG"; then
    echo "dtparam=i2s=on" | sudo tee -a "$CONFIG" > /dev/null
fi

if ! grep -q "^dtoverlay=max98357a,no-sdmode" "$CONFIG"; then
    echo "dtoverlay=max98357a,no-sdmode" | sudo tee -a "$CONFIG" > /dev/null
fi

echo
echo "MyVinyl setup complete."
echo
echo "Create a .env file with your Supabase configuration if you have not already."
echo "Then reboot the Raspberry Pi:"
echo
echo "    sudo reboot"
