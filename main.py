from discord_API import dcAPI, Channel # type: ignore
from modules import message_gather
import sqlite3
from time import time, sleep

### CONFIG
# Console                              (Console settings)
E_SILENT: bool = True                # Wont print errors to the console (there will be many)
S_SILENT: bool = False               # Wont print status updates to console 
FRAGILE: bool = False                # Will raise an exception if an error occurs (should only be used for debugging, and even then it's not recommended)

# Database                             (Database settings)
DATABASE_NAME: str = "main.sqlite"   # Database file name

# Data-gathering                       (Data gathering module ENABLEs)
GATHER_MESSAGES: bool = True         # Will gather messages from channels (either targeted or all) that you have access to

# Caching                              (Wont gather from certain servers if it's been gathered already, useful for gathering the first dataset) [WILL NOT WORK WITH TARGETED GATHERING]
CACHING_ENABLE: bool = False         # Whether or not caching should be enabled
CACHING_TIMEOUT: int = 86400000      # How long to cache data for in milliseconds (wont gather data from a cached guild until this timeout runs out)
CACHING_FILE: str = "cache.txt"      # Cache file name (.txt)

# Looping                              (Keep the script active forever)
LOOPING_ENABLE: bool = True          # Whether or not looping should be enabled
LOOPING_TIMEOUT: int = 30            # How long should the timeout be after a loop (seconds)
LOOPING_TIMES: int = 0               # How many times should the program loop until quitting (0 for infinite)

# Targeted gathering                   (Only target certain channels, useful for gathering data continously and ignoring announcement channels etc.)
TARGETED_ENABLE: bool = False        # Whether or not targeted gathering should be enabled, if not enabled, gets all channels
TARGETED_CHANNEL_FILE: str = "channels.txt" # File to read channel IDs from (insert 1 ID per line)

# Discord updates                      (Sends update messages to a predefined channel, useful for running on servers or other non-monitor computers)
NOTIFS_ENABLE: bool = False          # Whether or not discord updates should be enabled
NOTIFS_CHANNEL: int = 0              # Channel ID to send updates to
NOTIFS_FREQUENCY: int = 0            # How often to send updates (loop amount)

# Channel culling                      (Removes channels from the observed list that haven't had messages in a while)
CHANNEL_CULLING_ENABLE: bool = True  # Whether or not channel culling should be enabled
CHANNEL_CULLING_RANGE: int = 3600    # How old should the latest message in the channel be before it's considered dead (seconds)
CHANNEL_CULLING_CACHE: bool = True   # Will remember what channels are inactive and avoid them after restarts

# Misc                                 (Misc settings)
RATE_LIMIT_TIMEOUT: int = 600        # How many seconds to sleep for when hitting the rate-limit (0 for no sleeping, although that might get you stuck in a loop)

### END CONFIG

# Ensure files exist
print("[*] Checking files...")
open('token.txt', 'a').close()
open('inactive_channels.txt', 'a').close()
open(CACHING_FILE, 'a').close()
open(TARGETED_CHANNEL_FILE, 'a').close()

# Get static data and object references
print("[*] Setting up objects...")
with open("token.txt", "r") as file:
    TOKEN = file.read()
with open(TARGETED_CHANNEL_FILE, "r") as file:
    TARGETED_CHANNELS = file.read().splitlines()
with open("inactive_channels.txt", "r") as file:
    INACTIVE_CHANNELS = file.read().splitlines()
API = dcAPI(TOKEN, silent=E_SILENT, fragile=FRAGILE, rate_limit_timeout=RATE_LIMIT_TIMEOUT)
DATABASE = sqlite3.connect(DATABASE_NAME)

# Ensure tables exist
print("[*] Preparing database...")
DATABASE.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, channel_id INTEGER, author_id INTEGER, content TEXT, timestamp TEXT)")

# Misc setup
if not CHANNEL_CULLING_ENABLE:
    CHANNEL_CULLING_RANGE = 0

# Notepad
# TODO: make better configs (some yaml or something like that)
# TODO: make the DB add messages in batches instead of 1-by-1 to improve performance
# TODO: Add a config for the amount of messages to gather at once (currently max 50)
# TODO: remove caching since it's useless because of Channel Culling
# TODO: Gather old messages as well

sleep(1) # Discord rate limits the program if you start too fast...? (dunno but this about fixes it)

### Channel gathering
channels: list[Channel] = []
print("[*] Gathering channels...")
if not TARGETED_ENABLE:
    guilds = API.get_user_guilds()
    for guild in guilds:
        temp = API.get_guild_channels(guild)
        channels += temp
if TARGETED_ENABLE:
    counter = -1
    for channel_id in TARGETED_CHANNELS:
        counter += 1
        channels.append(Channel(int(channel_id), f"TARGETED_CHANNEL_{counter}"))
if CHANNEL_CULLING_ENABLE and CHANNEL_CULLING_CACHE:
    counter = 0
    for channel in channels:
        if channel.id in INACTIVE_CHANNELS:
            counter += 1
            channels.remove(channel)
    print("[?] Removed " + str(counter) + " inactive channels from list!")

print("[*] Setup complete!\n")

### Looping
start_time = time()
loop_number = 0
while True:
    loop_number += 1

    ### Modules here
    if CACHING_ENABLE and not TARGETED_ENABLE:
        # Ensure that cache file exists
        try:
            file = open(CACHING_FILE, "r")
            file.close()
        except FileNotFoundError:
            with open(CACHING_FILE, "w") as file:
                file.write("")

        # Search cache file for matching guild ID, if found, skip
        skip = False
        with open(CACHING_FILE, "r") as file:
            for line in file:
                if str(line.split(" ")[0]) == str(guild.id):
                    if time() - float(line.split()[1]) < CACHING_TIMEOUT:
                        print("Guild already in cache!", end="")
                        skip = True
                        break

        # Update cache
        with open(CACHING_FILE, "a") as file:
            file.write(f"{guild.id} {time()}\n")

        # Skip if necessary
        if skip:
            continue

    if GATHER_MESSAGES:
        channels = message_gather(API, DATABASE, channels, S_SILENT, channel_culling=CHANNEL_CULLING_RANGE, cull_cache=CHANNEL_CULLING_CACHE)

    if NOTIFS_ENABLE:
        if loop_number % NOTIFS_FREQUENCY == 0 and loop_number != 1:
            if not S_SILENT:
                print("[?] Sent update notification!")
            stored_messages_count = DATABASE.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            API.send_message(Channel(NOTIFS_CHANNEL, "None"), f"DATA GATHER UPDATE\n\nBeen running for {int((time() - start_time) / 60)} minutes\nLoop number: {loop_number}\nTotal stored messages: {stored_messages_count}")

    ### Break looping if not enabled or if looping times has been reached
    if not LOOPING_ENABLE:
        break
    if not S_SILENT:
        print(f"[?] Loop {loop_number} complete!")
    if loop_number >= LOOPING_TIMES and LOOPING_TIMES != 0:
        break
    sleep(LOOPING_TIMEOUT)

print("PROGRAM QUIT")