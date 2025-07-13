import board
import busio
import digitalio
import time
import RPi.GPIO as GPIO
import adafruit_ssd1306
import json
import os
import subprocess


# Rotary encoder GPIO pins
CLK = 27 # a
DT = 22 # b
SW = 17

# Date range limits
MIN_YEAR = 1996
MAX_YEAR = 2025

# OLED I2C display config
WIDTH = 128
HEIGHT = 64
I2C = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, I2C)

# Path to config file
CONFIG_PATH = "/home/pi/WaybackProxy/config.json"

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initial values
current_month = 1
current_year = 2005
formatted_date = ""  # YYYYMMDD format

def update_formatted_date():
    global formatted_date
    day = 1
    formatted_date = f"{current_year:04d}{current_month:02d}{day:02d}"

    # Load existing config if exists
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}

    # Update the date key
    config["DATE"] = formatted_date

    # Save back to config
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def update_display():
    oled.fill(0)
    oled.text(f"Month: {current_month:02d}", 0, 0, 1)
    oled.text(f"Year: {current_year}", 0, 15, 1)
    oled.text(f"{formatted_date}", 0, 40, 1)
    oled.show()

# Start-up state
last_clk = GPIO.input(CLK)
update_formatted_date()
update_display()

try:
    while True:
        clk_state = GPIO.input(CLK)
        dt_state = GPIO.input(DT)

        if clk_state != last_clk:
            if dt_state != clk_state:
                # Clockwise turn
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1
                    if current_year > MAX_YEAR:
                        current_year = MIN_YEAR
            else:
                # Counter-clockwise turn
                current_month -= 1
                if current_month < 1:
                    current_month = 12
                    current_year -= 1
                    if current_year < MIN_YEAR:
                        current_year = MAX_YEAR

            update_formatted_date()
            update_display()

        last_clk = clk_state
        def free_port(port):
            try:
                pid = subprocess.check_output(
                    f"lsof -t -i:{port}", shell=True
                ).decode().strip()
                if pid:
                    print(f"Killing PID {pid} on port {port}")
                    os.system(f"kill -9 {pid}")
            except subprocess.CalledProcessError:
                pass  # Nothing to kill

        # Button press to select date and restart proxy
        if GPIO.input(SW) == GPIO.LOW:
            update_formatted_date()

            oled.fill(0)
            oled.text("Restarting...", 0, 10, 1)
            oled.text(f"{formatted_date}", 0, 30, 1)
            oled.show()

        # Free port and restart service
            free_port(8080)  # or whatever port you're using
            subprocess.run(["sudo", "systemctl", "restart", "waybackproxy.service"])

            time.sleep(1)
            update_display()
            time.sleep(0.2)


except KeyboardInterrupt:
    GPIO.cleanup()
