from sqlite3 import Connection, IntegrityError
from datetime import datetime
from pytz import utc
from discord_API import dcAPI, Channel

def message_gather(API: dcAPI, DATABASE: Connection, channels: list[Channel], silent: bool = False, channel_culling: int = 0, cull_cache: bool = False):
    """Gathers message from all specified channels, returns an updated list of channels if channel_culling is enabled, returns the same list of channels if not."""
    updated_channels: list[Channel] = []
    for channel in channels:

        # Get messages, go through them and add them to the database
        messages = API.get_channel_messages(channel)
        for message in messages:
            try:
                message.content = message.content.replace("'", "")
                DATABASE.execute("INSERT INTO messages (id, channel_id, author_id, content, timestamp) VALUES (?, ?, ?, ?, ?)", (message.id, channel.id, message.author_id, message.content, message.timestamp))
            except IntegrityError: # Message already collected
                pass

        # Cull this channel if channel_culling is enabled (channel_culling != 0) and if there are messages
        if channel_culling != 0 and messages != []:
            # Timestamps are in format: YYYY-MM-DDTHH:MM:SS.000000+00:00
            # We can use the T as a separator for date and time (and discard milliseconds)
            try:
                time_obj = datetime.strptime(messages[0].timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
                time_now = datetime.now(utc)
                time_since = int((time_now - time_obj).total_seconds())
                if time_since < channel_culling: # All the non-culled channels go to updated_channels
                    updated_channels.append(Channel(channel.id, channel.name))
                else:
                    if not silent:
                        print("[*] Channel '" + channel.name + "' has been culled (last message was " + str(time_since) + " seconds ago)")
            except ValueError: # FIXME: time_obj sometimes throws ValueError, I don't know why, fix later, something to do with missing milliseconds I think
                pass
        elif channel_culling != 0: # Channel either has no messages or HTTP403'd (is private)
            if not silent:
                    print("[*] Channel '" + channel.name + "' has been culled (channel is private or empty)")
        
        # If cull_cache is enabled, update the cache file
        if cull_cache and channel_culling != 0:
            with open("inactive_channels.txt", "a") as f:
                if channel.id not in [c.id for c in updated_channels]:
                    f.write(str(channel.id) + "\n")

        # Print status, commit, and continue
        if not silent:
            print("[?] Channel '" + channel.name + "' done")
        DATABASE.commit()

    # Return the updated channel list (or normal list if channel_culling isnt enabled)
    if channel_culling == 0:
        updated_channels = channels
    return updated_channels