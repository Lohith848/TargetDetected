# Laptop Security Monitor

A lightweight Windows security tool that detects failed login attempts, captures a webcam photo of the intruder, and sends an alert with the photo and public IP address to a Telegram bot.

---

## Features

- Detects failed Windows login attempts (Event ID 4625)
- Captures a webcam photo immediately after detection
- Sends alert to Telegram with timestamp, public IP, and hostname
- Runs silently in the background via Windows Task Scheduler
- No admin privileges required after initial setup

---

## Requirements

- Windows 10 or 11
- Python 3.10+
- A Telegram bot token (via @BotFather)
- A webcam

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/laptop-security-monitor.git
cd laptop-security-monitor
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Create a `.env` file in the project folder**

```
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

To get your bot token, message @BotFather on Telegram and create a new bot.  
To get your chat ID, send any message to your bot and visit:
```
https://api.telegram.org/botYOUR_TOKEN/getUpdates
```
Look for `"chat": {"id": ...}` in the response.

**4. Add your account to the Event Log Readers group**

Run this once in CMD as Administrator:

```cmd
net localgroup "Event Log Readers" "YOUR_WINDOWS_USERNAME" /add
```

Then restart your PC.

---

## Running Manually

```cmd
cd C:\laptop-security-monitor
python monitor.py
```

---

## Auto-start with Task Scheduler

1. Open Task Scheduler and create a new task named `TargetDetected`
2. General tab: check `Run with highest privileges`, select `Run only when user is logged on`
3. Triggers tab: set trigger to `At log on` for your user account
4. Actions tab:
   - Program: full path to `pythonw.exe` (e.g. `C:\Python314\pythonw.exe`)
   - Arguments: `monitor.py`
   - Start in: full path to project folder
5. Conditions tab: uncheck `Start only if on AC power`
6. Click OK and restart your PC

---

## Project Structure

```
laptop-security-monitor/
├── monitor.py          # Main monitoring script
├── run_monitor.bat     # Optional batch launcher
├── requirements.txt    # Python dependencies
├── .env                # Your credentials (never commit this)
├── .gitignore          # Excludes .env, logs, and captured images
└── README.md
```

---

## Security Note

Never commit your `.env` file. It contains your Telegram bot token and chat ID. The `.gitignore` in this repo excludes it automatically.

---

## License

MIT License
