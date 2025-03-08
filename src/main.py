from discord_API import dcAPI, Channel # type: ignore
from logservice import GLOBAL_LOGSERVICE as LOGSRV
from modules import message_gather
from config import load_configs
from time import time, sleep
import sqlite3


# Notepad
# TODO: Add a config for the amount of messages to gather at once (currently max 50)
# TODO: Gather old messages as well
# TODO: Threading


# Load config and format them into CONSTANTS
configs = load_configs()
try: # mmmmm I love massive type: ignore checks
    ERROR_SILENT: bool =            configs["error_silent"]             # type: ignore
    INFO_SILENT: bool =             configs["info_silent"]              # type: ignore
    ACTION_SILENT: bool =           configs["action_silent"]            # type: ignore
    STATUS_SILENT: bool =           configs["status_silent"]            # type: ignore
    FRAGILE: bool =                 configs["fragile"]                  # type: ignore
    DATABASE_NAME: str =            configs["database_name"]            # type: ignore
    GATHER_MESSAGES: bool =         configs["gather_messages"]          # type: ignore
    LOOPING_ENABLE: bool =          configs["looping_enable"]           # type: ignore
    LOOPING_TIMEOUT: int =          configs["looping_timeout"]          # type: ignore
    LOOPING_TIMES: int =            configs["looping_times"]            # type: ignore
    TARGETED_ENABLE: bool =         configs["targeted_enable"]          # type: ignore
    TARGETED_CHANNEL_FILE: str =    configs["targeted_channel_file"]    # type: ignore
    NOTIFS_ENABLE: bool =           configs["notifs_enable"]            # type: ignore
    NOTIFS_CHANNEL: int =           configs["notifs_channel"]           # type: ignore
    NOTIFS_FREQUENCY: int =         configs["notifs_frequency"]         # type: ignore
    CHANNEL_CULLING_ENABLE: bool =  configs["channel_culling_enable"]   # type: ignore
    CHANNEL_CULLING_RANGE: int =    configs["channel_culling_range"]    # type: ignore
    CHANNEL_CULLING_CACHE: bool =   configs["channel_culling_cache"]    # type: ignore
    RATE_LIMIT_TIMEOUT: int =       configs["rate_limit_timeout"]       # type: ignore
except IndexError:
    print("[!] Config file is outdated or corrupt, delete the config file to reset it")
    raise Exception("[!] Config file is outdated or corrupt, delete the config file to reset it")

# Apply configs
LOGSRV.ERROR_SILENT = ERROR_SILENT
LOGSRV.ACTION_SILENT = ACTION_SILENT
LOGSRV.INFO_SILENT = INFO_SILENT
LOGSRV.STATUS_SILENT = STATUS_SILENT

# Ensure files exist
LOGSRV.log("Checking files...", "action")
open('data/token.txt', 'a').close()
open('data/inactive_channels.txt', 'a').close()
open(TARGETED_CHANNEL_FILE, 'a').close()

# Get static data and object references
LOGSRV.log("Setting up objects...", "action")
with open("data/token.txt", "r") as file:
    TOKEN = file.read()
with open(TARGETED_CHANNEL_FILE, "r") as file:
    TARGETED_CHANNELS = file.read().splitlines()
with open("data/inactive_channels.txt", "r") as file:
    INACTIVE_CHANNELS = file.read().splitlines()
API = dcAPI(TOKEN, silent=ERROR_SILENT, fragile=FRAGILE, rate_limit_timeout=RATE_LIMIT_TIMEOUT)

# Ensure tables exist
LOGSRV.log("Preparing database...", "action")
DATABASE = sqlite3.connect(DATABASE_NAME)
DATABASE.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, channel_id INTEGER, author_id INTEGER, content TEXT, timestamp TEXT)")

# Misc setup
if not CHANNEL_CULLING_ENABLE:
    CHANNEL_CULLING_RANGE = 0 # type: ignore (It should be 0 anyway if it's off, this is here to just make sure it is)

sleep(1) # Discord rate limits the program if you start too fast

### Channel gathering
channels: list[Channel] = []
LOGSRV.log("Gathering channels...", "action")
if not TARGETED_ENABLE:
    guilds = API.get_user_guilds()
    for guild in guilds:
        temp = API.get_guild_channels(guild)
        channels.extend(temp)
if TARGETED_ENABLE:
    counter = -1
    for channel_id in TARGETED_CHANNELS:
        counter += 1
        channels.append(Channel(int(channel_id), f"TARGETED_CHANNEL_{counter}"))
if CHANNEL_CULLING_ENABLE and CHANNEL_CULLING_CACHE:
    counter = 0
    updated_channels: list[Channel] = []
    for channel in channels:
        if str(channel.id) in INACTIVE_CHANNELS:
            counter += 1
        else:
            updated_channels.append(channel)
    channels = updated_channels
    LOGSRV.log("Removed " + str(counter) + " inactive channels from list!")
LOGSRV.log(str(len(channels)) + " channels gathered!")
LOGSRV.log("Setup complete!\n")

### Looping
start_time = time()
loop_number = 0
while True:
    loop_number += 1

    ### Modules here
    if GATHER_MESSAGES:
        channels = message_gather(API, DATABASE, channels, channel_culling=CHANNEL_CULLING_RANGE, cull_cache=CHANNEL_CULLING_CACHE)

    if NOTIFS_ENABLE:
        if loop_number % NOTIFS_FREQUENCY == 0 and loop_number != 1:
            LOGSRV.log("Sent update notification!")
            stored_messages_count = DATABASE.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            API.send_message(Channel(NOTIFS_CHANNEL, "None"), f"DATA GATHER UPDATE\n\nBeen running for {int((time() - start_time) / 60)} minutes\nLoop number: {loop_number}\nTotal stored messages: {stored_messages_count}")

    ### Break looping if not enabled or if looping times has been reached
    if not LOOPING_ENABLE:
        break    
    if loop_number >= LOOPING_TIMES and LOOPING_TIMES != 0:
        break
    LOGSRV.log(f"Loop {loop_number} complete!\n")
    sleep(LOOPING_TIMEOUT)

LOGSRV.log("Program quit!")
DATABASE.close()