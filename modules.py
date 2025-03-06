from sqlite3 import Connection, IntegrityError
from discord_API import dcAPI, Channel

def message_gather(API: dcAPI, DATABASE: Connection, channels: list[Channel], silent: bool = False):
    """Gathers message from all specified channels"""
    for channel in channels:
        messages = API.get_channel_messages(channel)
        for message in messages:
            try:
                message.content = message.content.replace("'", "")
                DATABASE.execute("INSERT INTO messages (id, channel_id, author_id, content, timestamp) VALUES (?, ?, ?, ?, ?)", (message.id, channel.id, message.author_id, message.content, message.timestamp))
            except IntegrityError:
                pass
        if not silent:
            print("[?] Channel '" + channel.name + "' done")
        DATABASE.commit()