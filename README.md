# twitch_bot

A simple Twitch bot that can be used to interact with chat. It is intended to be used with OBS.

## Installation

1. Clone the repository
2. Install the required packages with `pip install -r requirements.txt`
3. Create a `.env` file in the root directory from the `.env.example` file and fill in the required information
4. Run the bot with `python3 twitch_bot.py`

## Features

### Chat display

It displays the chat messages as it was a debian terminal.

The bot will create 2 files in the root directory:

- latest_chat.txt: contains the latest chat messages
- latest_chat.html: contains the latest chat messages in HTML format

The messages are displayed in the following format:

```text
{channel}@twitch:~/{username}$ {message}
```

For html format, the last line displays an empty "command" line with a blinking cursor.
