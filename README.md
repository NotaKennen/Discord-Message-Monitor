# Discord Message Monitor
The Discord message monitor is a self-bot tool to automatically gather and store messages in a convenient database. It's purpose is to work as a data-analysis tool so you can analyze any messages sent in any of your servers. It does NOT go through old messages (although that is planned, might still never make it), so it will only actively monitor newer messages, specifically the newest 50 messages will be grabbed on each channel check.

## Usage
To use the monitor, you can simply run the main.py file. After that, it'll create some necessary files, mainly "token.txt", you should put an account's token here. The account can be anything, preferably a burner account (since there is a non-zero chance the account might get banned), you just need to join to servers you want to monitor with the account.

Once you run it for the first time, it'll run the first loop in "culling mode", where it'll check every single channel in every single server, and cache all the inaccessible and dead ones so it doesn't need to check them on later runs. After that, it'll only check channels that have had some message activity in the last week. Most of the things mentioned here are configurable (such as whether or not it should cull dead channels, if you dont want to loop it, if you want to cache dead channels etc etc etc), read the Config section for more information. 

After running it for a while, it'll have gathered a decent amount of messages into an SQLite database. You can then use these however you will. Currently it'll format the database like this: Message ID / User ID / Channel ID / Content / Timestamp (Discord formatted, YYYY-MM-DDTHH:MM:SS.000000+00:00, the T between the Date and Time is a good separator if you want to format it).

## Config
The program will create a config file when running for the first time, here is an explanation of all the config options:

### Console:
- error_silent (bool): Whether or not errors should be printed to the console ([!])
- info_silent (bool): Whether or not info messages should be printed to the console ([?])
- action_silent (bool): Whether or not action messages should be printed to the console ([*])
- status_silent (bool): Whether or not status messages should be printed to the console ([-])
- fragile (bool): If True, raises an exception on errors (should only be used when using channel_culling, even then not recommended)

### Database
- database_name (str): The name for the database file
  
### Modules: 
- gather_messages (bool): Enable for the gather_messages module

### Looping:
- looping_enable (bool): Toggle for looping
- looping_timeout (int): How long should the program sleep after a loop
  
### Targeting
- targeted_enable (bool): Toggle for targeting
- targeted_channel_file (str): A file filled with channel IDs (separated by newlines) for the targeted channels

### Notifications
- notifs_enable (bool): Toggle for notifications
- notifs_channel (int): Channel ID where the notifications will be sent
- notifs_frequency (int): How often should a notification be sent (loops)

### Channel Culling
- channel_culling_enable (bool): Toggle for channel culling
- channel_culling_range (int): How long until a channel is marked as dead (seconds since latest message)
- channel_culling cache (bool): Toggle for caching the culled channels so they dont have to be collected twice

### Misc
- rate_limit_timeout (int): How long the program should sleep for if it hits the Discord rate limit