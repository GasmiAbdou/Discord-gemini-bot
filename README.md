# Discord-Free-ChatBot

## Requirements

- discord.py
- aiohttp
- Google's generativeai library


### Installation

1. Clone the repository to your local machine.
2. Install the required Python libraries:

   ```
   pip install -r requirements.txt
   ```
The bot will start listening to messages in your Discord server. It responds to direct mentions or direct messages.

## Configuration

Edit the `main.py` file must include:

- `DISCORD_BOT_TOKEN`: Your Discord bot token.
- `GOOGLE_AI_KEY`: Your Google AI API key. Google API Key can be acquired from https://makersuite.google.com/
- `MAX_HISTORY`: The maximum number of messages to retain in history for each user. 0 will disable history

then run `main.py`

## Commands

- **Mention or DM the bot to activate:** History only works on pure text input 
- **Send an Image:** The bot will respond with an AI-generated interpretation or related content.
- **Type 'RESET' or /reset:** Clears the message history for the user.
- ** /set_chatbot** to toggle chatbot channel for atoresponding without mention the bot !
