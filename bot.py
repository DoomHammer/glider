import logging
import os
import traceback

import aiocron
import discord
from dotenv import load_dotenv
import requests

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
space_edpoint = os.getenv('SPACE_ENDPOINT')

avatars = {}

usernames = {
    'closed': 'Space zamknięty',
    'open': 'Space otwarty'
}

online_status = {
    'closed': discord.Status.offline,
    'open': discord.Status.online
}

current_state = None

# Logging configuration
logging.basicConfig(level=logging.INFO)

client = discord.Client()

async def update_presence(state):
    global current_state
    if state != current_state:
        current_state = state
        if client.user:
            logging.info(f'Updating the presence to "{state}"')
            await client.change_presence(activity=discord.Activity(name=f"the Space (*{state}*)", type=discord.ActivityType.watching))
            try:
                await client.user.edit(avatar=avatars[state])
            except:
                logging.error(traceback.format_exc())
            for guild in client.guilds:
                member = guild.get_member_named(client.user.name)
                await member.edit(nick=usernames[state])

# Fire every minute
@aiocron.crontab('* * * * *')
async def is_there_life_on_mars():
    logging.info('Checking the status')
    space_state = requests.get(space_edpoint).json()['status']
    logging.info(f'Current status: {space_state}')
    await update_presence(space_state)

@client.event
async def on_ready():
    for guild in client.guilds:
        logging.info(f'{client.user} has connected to Discord server {guild}!')
    for state in ['closed', 'open']:
        with open(f'res/glider_{state}.png', 'rb') as avatar:
            avatars[state] = avatar.read()
    try:
        await client.user.edit(username='glider')
    except:
        logging.error(traceback.format_exc())
    await update_presence('closed')

client.run(discord_token)