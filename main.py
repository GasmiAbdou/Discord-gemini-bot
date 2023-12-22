import PyPDF2
import aiohttp
import asyncio
import discord
import docx
import io
import io
import json
import os
import random
import re
import threading
import urllib
from discord.ext import commands
from dotenv import load_dotenv
import re
from discord.ext import commands
from discord import Embed, app_commands
from discord.ext import commands
from gasmii import text_model, image_model

import discord
import google.generativeai as genai

from dotenv import load_dotenv

message_history = {}
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, heartbeat_timeout=60)

load_dotenv()

GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAX_HISTORY = int(os.getenv("MAX_HISTORY"))
#CUSTOM_PERSONALITY = os.getenv("CUSTOM_PERSONALITY") --- this shit is disgusting asf and booring old skill for custom personality fuck it and fuck you if u enable it (gonna update it soon & set chatbo)






bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    await bot.tree.sync()
    num_commands = len(bot.commands)
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(),
        scopes=("bot", "applications.commands")
    )

    def print_in_color(text, color):
        return f"\033[{color}m{text}\033[0m"

    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')

    ascii_art = """
    \033[1;35m
    
███████╗██████╗ ███████╗██╗  ██╗████████╗██████╗ ██╗   ██╗███╗   ███╗
██╔════╝██╔══██╗██╔════╝██║ ██╔╝╚══██╔══╝██╔══██╗██║   ██║████╗ ████║
███████╗██████╔╝█████╗  █████╔╝    ██║   ██████╔╝██║   ██║██╔████╔██║
╚════██║██╔═══╝ ██╔══╝  ██╔═██╗    ██║   ██╔══██╗██║   ██║██║╚██╔╝██║
███████║██║     ███████╗██║  ██╗   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║
╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝
                                                                     
\033[0m
    """

    print(ascii_art)
    print(print_in_color(f"{bot.user} aka {bot.user.name} has connected to Discord!", "\033[1;97"))
    print(print_in_color(f"  Loaded {num_commands} commands", "1;35"))
    print(print_in_color(f"      Invite link: {invite_link}", "1;36"))


# Function to generate response based on custom personality prompts





@bot.hybrid_command(name="reset", description="Clears bot message history")
async def reset(ctx):
    global message_history
    message_history = {}
    await ctx.send("🤖 Bot message history has been cleared.")

    
def create_chatbot_channels_file():
    if not os.path.exists('chatbot_channels.json'):
        with open('chatbot_channels.json', 'w') as file:
            json.dump({}, file)

create_chatbot_channels_file()

chatbot_channels_file = 'chatbot_channels.json'
chatbot_channels = {}

# Load chatbot channels from chatbot_channels.json if it exists
if os.path.exists(chatbot_channels_file):
    with open(chatbot_channels_file, 'r') as file:
        chatbot_channels = json.load(file)

# Command to set or toggle chatbot channel
@bot.hybrid_command(name="set_chatbot", description="Set or toggle chatbot channel")
async def set_chatbot(ctx, channel: discord.TextChannel):
    if ctx.guild is None:
        await ctx.send("This command can only be used in a server.")
        return

    guild_id = str(ctx.guild.id)

    with open(chatbot_channels_file, 'r') as file:
        chatbot_channels = json.load(file)

    if guild_id in chatbot_channels:
        if chatbot_channels[guild_id]['channel_id'] == str(channel.id):
            del chatbot_channels[guild_id]
            await ctx.send(f"Chatbot responses have been toggled off for #{channel.name}.")
        else:
            chatbot_channels[guild_id] = {'channel_id': str(channel.id)}
            await ctx.send(f"Chatbot responses have been set for #{channel.name}.")
    else:
        chatbot_channels[guild_id] = {'channel_id': str(channel.id)}
        await ctx.send(f"Chatbot responses have been set for #{channel.name}.")

    with open(chatbot_channels_file, 'w') as file:
        json.dump(chatbot_channels, file, indent=4)

# Event handler for new messages
@bot.event
async def on_message(message):
    # Ignore messages sent by the bot
    if message.author == bot.user:
        return
    # Check if the bot is mentioned or the message is a DM
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        #Start Typing to seem like something happened
        cleaned_text = clean_discord_message(message.content)

        async with message.channel.typing():
            # Check for image attachments
            if message.attachments:
                print("New Image Message FROM:" + str(message.author.id) + ": " + cleaned_text)
                #Currently no chat history for images
                for attachment in message.attachments:
                    #these are the only image extentions it currently accepts
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                        await message.add_reaction('🎨')

                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment.url) as resp:
                                if resp.status != 200:
                                    await message.channel.send('Unable to download the image.')
                                    return
                                image_data = await resp.read()
                                response_text = await generate_response_with_image_and_text(image_data, cleaned_text)
                                #Split the Message so discord does not get upset
                                await split_and_send_messages(message, response_text, 1700)
                                return
            #Not an Image do text response
            else:
                print("New Message FROM:" + str(message.author.id) + ": " + cleaned_text)
                #Check for Keyword Reset
                if "RESET" in cleaned_text:
                    #End back message
                    if message.author.id in message_history:
                        del message_history[message.author.id]
                    await message.channel.send("🤖 History Reset for user: " + str(message.author.name))
                    return
                await message.add_reaction('💬')

                #Check if history is disabled just send response
                if(MAX_HISTORY == 0):
                    response_text = await generate_response_with_text(cleaned_text)
                    #add AI response to history
                    await split_and_send_messages(message, response_text, 1700)
                    return;
                #Add users question to history
                update_message_history(message.author.id,cleaned_text)
                response_text = await generate_response_with_text(get_formatted_message_history(message.author.id))
                #add AI response to history
                update_message_history(message.author.id,response_text)
                #Split the Message so discord does not get upset
                await split_and_send_messages(message, response_text, 1700)


    

#ry-------------------------------------------------

async def generate_response_with_text(message_text):
    prompt_parts = [message_text]
    print("Got textPrompt: " + message_text)
    response = text_model.generate_content(prompt_parts)
    if(response._error):
        return "❌" +  str(response._error)
    return response.text

async def generate_response_with_image_and_text(image_data, text):
    image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
    prompt_parts = [image_parts[0], f"\n{text if text else 'What is this a picture of?'}"]
    response = image_model.generate_content(prompt_parts)
    if(response._error):
        return "❌" +  str(response._error)
    return response.text

#---------------------------------------------Message History-------------------------------------------------
def update_message_history(user_id, text):
    # Check if user_id already exists in the dictionary
    if user_id in message_history:
        # Append the new message to the user's message list
        message_history[user_id].append(text)
        # If there are more than 12 messages, remove the oldest one
        if len(message_history[user_id]) > MAX_HISTORY:
            message_history[user_id].pop(0)
    else:
        # If the user_id does not exist, create a new entry with the message
        message_history[user_id] = [text]

def get_formatted_message_history(user_id):
    """
    Function to return the message history for a given user_id with two line breaks between each message.
    """
    if user_id in message_history:
        # Join the messages with two line breaks
        return '\n\n'.join(message_history[user_id])
    else:
        return "No messages found for this user."

#---------------------------------------------Sending Messages-------------------------------------------------
async def split_and_send_messages(message_system, text, max_length):

    # Split the string into parts
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i:i+max_length]
        messages.append(sub_message)

    # Send each part as a separate message
    for string in messages:
        await message_system.channel.send(string)

def clean_discord_message(input_string):
    # Create a regular expression pattern to match text between < and >
    bracket_pattern = re.compile(r'<[^>]+>')
    # Replace text between brackets with an empty string
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content




#---------------------------------------------Run Bot-------------------------------------------------
bot.run(DISCORD_BOT_TOKEN)