import os
import irc.bot
import irc.client
from collections import deque
from dotenv import load_dotenv
import re
import html.entities
from obs_bot import ObsBot
import asyncio

# Load environment variables from .env file
load_dotenv()

class ChatBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        # Load credentials from environment variables
        username = os.getenv("TWITCH_BOT_USERNAME")
        token = os.getenv("TWITCH_BOT_TOKEN")
        channel = os.getenv("TWITCH_CHANNEL")
        
        server = 'irc.chat.twitch.tv'
        port = 6667
        super().__init__([(server, port, token)], username, username)

        # OBS setup
        self.obs = ObsBot()
        
        # IRC and channel setup
        self.channel = '#' + channel
        self.username = channel
        
        # Files and message buffers
        self.channel_name = channel
        self.text_message_file = "output/latest_chat.txt"
        self.html_message_file = "output/latest_chat.html"
        self.recent_messages_text = [' ' * 90] * 28
        self.recent_messages_html = deque([''] * 27, maxlen=27)  # Reserve one slot for the blinker line
        self.line_counter = 0  # Counter for initial text message filling

    def on_welcome(self, connection, event):
        connection.join(self.channel)
        print(f'Joined {self.channel}')

    def on_pubmsg(self, connection, event):
        message = event.arguments[0]
        user = event.source.nick

        # Respond to specific commands
        self._process_command(message)
        
        # Format messages for text and HTML
        formatted_text_message = f"{self.channel_name}@twitch:~/{user}$ {message}"
        
        # Split messages and add to buffers
        self._process_text_message(formatted_text_message)
        self._process_html_message(message, user)

        # Write updated messages to files
        self._write_text_file()
        self._write_html_file()

        # Write the latest messages as an HTML file
        self._write_html_file()

    def start_bot(self):
        self.start()

    def _process_command(self, message):
        """Handles command messages for the bot."""
        if message.lower() == 'ping':
            self.connection.privmsg(self.channel, 'pong')
        elif message.lower() == 'hello':
            self.connection.privmsg(self.channel, f'Hello, {self.username}!')
        elif message.lower() == 'goodbye':
            self.connection.privmsg(self.channel, f'Goodbye, {self.username}!')
        elif message.lower() == 'kill me sarah':
            self.die()
        elif message.lower() == '!scene':
            current_scene = self.obs.getCurrentScene()
            self.connection.privmsg(self.channel, f'Current scene: {current_scene}')
        elif message.lower().startswith('!setscene'):
            scene_name = message.split(' ')[1]
            self.obs.setScene(scene_name)
        elif message.lower() == '!petcam':
            self.obs.switch_scene_in_background('Start_pets', 8)
        elif message.lower() == '!chat':
            self.obs.switch_scene_in_background('Start_chat', 8)
        elif message.lower() == '!allscenes':
            all_scenes = self.obs.getAllScenes()
            scene_names = [scene['sceneName'] for scene in all_scenes]
            self.connection.privmsg(self.channel, f'All scenes: {", ".join(scene_names)}')

    def _process_text_message(self, message):
        """Handles text message formatting and storage for .txt output."""
        while len(message) > 90:
            part = message[:90]
            last_space = part.rfind(' ')
            if last_space != -1:
                part = message[:last_space]
                message = message[last_space + 1:]
            else:
                message = message[90:]
            self._add_text_message(part)
        
        if message:
            self._add_text_message(message)

    def _add_text_message(self, message):
        padded_message = message.ljust(90)
        if self.line_counter < 28:
            self.recent_messages_text[self.line_counter] = padded_message
            self.line_counter += 1
        else:
            self.recent_messages_text.pop(0)
            self.recent_messages_text.append(padded_message)

    def _write_text_file(self):
        with open(self.text_message_file, "w") as file:
            file.write("\n".join(self.recent_messages_text))

    def _process_html_message(self, message, user):
        """Handles HTML message formatting and storage for .html output."""
        split_messages = self._split_html_message(message, user)
        for part in split_messages:
            self._add_html_message(part)

    def _split_html_message(self, plain_text, user):
        """Split the message text into parts of max 50 characters, adding prefix only to the first part."""
        split_messages = []
        prefix_html = f"""
            <span class="prefix">{self.username}@twitch</span>:<span class="username">~/{user}</span>$ 
        """
        prefix_length = len(self._strip_html_tags(prefix_html).strip())
        available_length_first_line = 50 - prefix_length

        # First line: account for prefix length
        if len(plain_text) <= available_length_first_line:
            # If the message fits on one line with the prefix, add it directly
            split_messages.append(f"{prefix_html}<span class=\"text\">{plain_text}</span>")
            return split_messages

        # Otherwise, split at the last space within the available length for the first line
        first_part = plain_text[:available_length_first_line]
        last_space = first_part.rfind(' ')

        if last_space != -1:
            # Split at the last space for a clean break
            first_part = plain_text[:last_space]
            plain_text = plain_text[last_space + 1:]
        else:
            # If no space, split strictly at the available length
            plain_text = plain_text[available_length_first_line:]

        # Add the first line with the prefix
        split_messages.append(f"{prefix_html}<span class=\"text\">{self.convert_to_html_entities(first_part)}</span>")

        # Handle the remaining parts without the prefix
        while len(plain_text) > 50:
            part = plain_text[:50]
            last_space = part.rfind(' ')
            
            if last_space != -1:
                # Split at the last space for a clean break
                part = plain_text[:last_space]
                plain_text = plain_text[last_space + 1:]
            else:
                # If no space, split strictly at 50 characters
                plain_text = plain_text[50:]

            # Add each subsequent part wrapped in text span
            split_messages.append(f"""
                <span class="text">{self.convert_to_html_entities(part)}</span>
            """)

        # Add any remaining part of the message
        if plain_text:
            split_messages.append(f"""
                <span class="text">{self.convert_to_html_entities(plain_text)}</span>
            """)

        return split_messages


    def _strip_html_tags(self, text):
        return re.sub('<[^<]+?>', '', text)

    def _add_html_message(self, message):
        self.recent_messages_html.append(message)

    @staticmethod
    def convert_to_html_entities(text):
        # Create a mapping for common accented characters to HTML entities
        entity_text = ""
        for char in text:
            # Convert each character to its named entity, if available
            entity = html.entities.codepoint2name.get(ord(char))
            if entity:
                # If there's an HTML entity, use it
                entity_text += f"&{entity};"
            else:
                # Otherwise, keep the character as-is
                entity_text += char
        return entity_text

    def _write_html_file(self):
        html_content = """
<!DOCTYPE html>
<html>
    <head>
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=fira-code:400" rel="stylesheet" />
        <meta charset="UTF-8">
        <title>{self.username} Twitch Chat</title>
        <style>
            body { font-family: 'Fira Code', monospace; color: white; background-color: black; }
            .message { font-size: 17px; margin: 2px 0; }
            .prefix { color: #c83a5b; }
            .username { color: #8ed250; }
            .text { color: #FFFFFF; }
            .blinker { font-weight: bold; color: #FFFFFF; animation: blink 1s step-start infinite; }
            @keyframes blink { 50% { opacity: 0; } }
        </style>
        <script>
            setTimeout(function() { window.location.reload(); }, 2000);
        </script>
    </head>
    <body>
        """
        non_empty_messages = [msg for msg in self.recent_messages_html if msg.strip()]
        for msg in non_empty_messages:
            # Use the static method to convert to HTML entities
            html_content += f"""
        <div class="message">{msg}</div>\n
            """
        
        blinker_line = f"""
        <div class="message"><span class="prefix">{self.username}@twitch</span>:<span class="username">~</span>$ <span class="blinker">_</span></div>
        """
        html_content += blinker_line
        remaining_lines = 28 - len(non_empty_messages) - 1
        html_content += """
        <div class=\"message\">&nbsp;</div>\n
        """ * remaining_lines
        html_content += """
    </body>
</html>
        """

        with open(self.html_message_file, "w", encoding="utf-8") as file:
            file.write(html_content)

# Function to run the bot
def run_chat_bot():
    bot = ChatBot()
    bot.start_bot()
