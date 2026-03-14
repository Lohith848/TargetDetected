# ============================================================
#  Laptop Security Monitor v2.0
#  Detects failed logins, captures webcam photo,
#  sends alert + IP + image to Telegram bot.
# ============================================================

import time
import requests
import socket
import subprocess
import cv2
import os
import logging
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
BOT_TOKEN = "8269865619:AAGJAANp3DmtWFfG4sTdM1KTKM4BvuGEV3A"
CHAT_ID   = "7722428088"
SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
LOG_FILE      = os.path.join(SCRIPT_DIR, "monitor.log")
CAPTURE_FILE  = os.path.join(SCRIPT_DIR, "intruder.jpg")
POLL_INTERVAL = 3
COOLDOWN      = 60

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log(msg, level="info"):
    print(msg)
    getattr(logging, level)(msg)

# ── WEBCAM ────────────────────────────────────────────────────────────────────
def capture_image(path):
    """
    Opens camera only when called, flushes buffer fast,
    captures one frame, then closes immediately.
    Camera is OFF the rest of the time.
    """
    cam = None
    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cam.isOpened():
            log("Webcam not accessible.", "warning")
            return False

        # Fast flush — read frames rapidly to clear dark buffer frames
        for _ in range(10):
            cam.read()

        # Short pause for exposure to settle
        time.sleep(0.8)

        # Take the actual photo
        ret, frame = cam.read()

        if ret:
            cv2.imwrite(path, frame)
            size = os.path.getsize(path)
            log(f"Image captured -> {path} ({size} bytes)")
            return True
        else:
            log("Failed to read frame from webcam.", "warning")
            return False

    except Exception as e:
        log(f"capture_image error: {e}", "error")
        return False
    finally:
        # Always close the camera
        if cam and cam.isOpened():
            cam.release()
            log("Webcam closed.")

# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text.strip()
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "Unknown"

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(text):
    try:
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        log(f"sendMessage: {response.status_code}")
    except Exception as e:
        log(f"send_message error: {e}", "error")

def send_photo(path, caption=""):
    try:
        if not os.path.exists(path):
            log(f"Photo not found: {path}", "error")
            return
        size = os.path.getsize(path)
        log(f"Sending photo ({size} bytes)...")
        with open(path, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"},
                files={"photo": f},
                timeout=30,
            )
        log(f"sendPhoto: {response.status_code} - {response.text[:120]}")
        if not response.ok:
            log("sendPhoto failed, trying sendDocument...", "warning")
            with open(path, "rb") as f:
                response2 = requests.post(
                    f"{BASE_URL}/sendDocument",
                    data={"chat_id": CHAT_ID, "caption": caption},
                    files={"document": f},
                    timeout=30,
                )
            log(f"sendDocument: {response2.status_code} - {response2.text[:120]}")
    except Exception as e:
        log(f"send_photo error: {e}", "error")

# ── EVENT LOG ─────────────────────────────────────────────────────────────────
_last_seen_record = -1

def get_latest_4625_record():
    try:
        ps_cmd = (
            "Get-WinEvent -LogName Security -FilterXPath "
            "'*[System[EventID=4625]]' -MaxEvents 1 "
            "| Select-Object -ExpandProperty RecordId"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        output = result.stdout.strip()
        if output.isdigit():
            return int(output)
        return -1
    except Exception as e:
        log(f"get_latest_4625_record error: {e}", "error")
        return -1

def check_failed_logins():
    global _last_seen_record
    try:
        current = get_latest_4625_record()
        if current == -1:
            return False
        if _last_seen_record == -1:
            _last_seen_record = current
            log(f"Anchored at event record #{_last_seen_record}")
            return False
        if current > _last_seen_record:
            _last_seen_record = current
            return True
        return False
    except Exception as e:
        log(f"check_failed_logins error: {e}", "error")
        return False

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    log("=== Security Monitor v2.0 Started ===")

    while True:
        try:
            if check_failed_logins():
                ts        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                public_ip = get_public_ip()

                log(f"Failed login detected at {ts}  IP: {public_ip}")

                alert_text = (
                    f"⚠️ <b>Failed Login Detected!</b>\n\n"
                    f"🕐 <b>Time :</b> {ts}\n"
                    f"🌐 <b>Public IP :</b> <code>{public_ip}</code>\n"
                    f"💻 <b>Host :</b> {socket.gethostname()}"
                )
                send_message(alert_text)

                if capture_image(CAPTURE_FILE):
                    send_photo(
                        CAPTURE_FILE,
                        caption=f"Intruder captured at {ts}\nIP: {public_ip}",
                    )
                else:
                    send_message("Could not capture webcam image.")

                time.sleep(COOLDOWN)

        except Exception as e:
            log(f"Main loop error: {e}", "error")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()