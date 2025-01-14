import discord
import time
import asyncio
import sys
from Implementation import YouTuber
from config import Config
from pathlib import Path
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

config = Config(Path(sys.argv[1] if len(sys.argv) > 1 else 'config.yml'))
client = discord.Client(intents=intents)
youtubers = config.getYouTubersList() if (config.getYouTubersNr() != 0) else sys.exit()
if (config.getDiscordChannelNr() == 0): sys.exit()
id = ''

GOOGLE_API: str = os.environ.get('DYN_YOUTUBE_DATA_V3_API_TOKEN', None)
DiscordAPIToken: str = os.environ.get('DYN_DISCORD_API_TOKEN', None)

if not GOOGLE_API:
    print("ERROR: Missing YouTube API v3 key in env:DYN_YOUTUBE_DATA_V3_API_TOKEN!")
    sys.exit(1)

if not DiscordAPIToken:
    print("ERROR: Missing Discord bot token in env:DYN_DISCORD_API_TOKEN!")
    sys.exit(1)

pingEveryXMinutes = config.getPingTime()
threads = []
processes = []

i = 0
while i < config.getYouTubersNr():
    temp_list = []
    temp_list.append(config.getYouTubersList()[i]['name'])
    temp_list.append(id) if not config.getYouTubersList()[i]['channelID'] else temp_list.append(config.getYouTubersList()[i]['channelID'])
    temp_list.append(True) if not id else temp_list.append(False)
    temp_list.append('')
    threads.append(temp_list)
    i += 1

i = 0

while i < config.getYouTubersNr():
    processes.append(YouTuber(GOOGLE_API, threads[i][1], threads[i][2]))
    i += 1

async def update():
    while True:
        try:
            waittime = pingEveryXMinutes * 60
            for item in config.getYouTubersNr():
                data = processes[item].update()
                if processes[item].isUserLive():
                    if not processes[item].liveId == threads[item][3]:
                        print('{} IS LIVESTREAMING NOW! PUSHING UPDATE ON DISCORD.'.format(threads[item][0]))
                        threads[item][3] = processes[item].liveId
                        videoLink = processes[item].getVideoLink(processes[item].getUserLiveData())
                        for x in range (0, config.getDiscordChannelNr()):
                            livestream = config.getDiscordChannelList()[x]['Livestream'].format(threads[item][0]) + '\n{}'.format(videoLink)
                            channelID = config.getDiscordChannelList()[x]['channelID']
                            print(channelID)
                            await client.get_channel(channelID).send(livestream)

        except:
            pass
        while waittime > 0:
            mins, secs = divmod(waittime, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            sys.stdout.write('Rechecking in ' + str(timeformat) + '\r')
            waittime -= 1
            await asyncio.sleep(1)

@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('---------------------------------------')
    print('Bot running.')
    asyncio.ensure_future(update())

client.run(DiscordAPIToken)
