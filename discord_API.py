import requests # type: ignore
from time import sleep

class Message:
    def __init__(self, id: int, author: str, author_id: int, content: str, timestamp: str):
        self.id: int = id
        self.author: str = author
        self.author_id: int = author_id
        self.content: str = content
        self.timestamp: str = timestamp
        
class Channel:
    def __init__(self, id: int, name: str):
        self.name = name
        self.id = id

class Guild:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
    
class User:
    def __init__(self, token: str):
        self.token = token

    def _get(self) -> dict[str, str|int]:
        return {}
    
class dcAPI:
    """
    Python API to interact with the Discord user API, is able to get messages, channels and guilds as well as send messages.

    token: The token to use for authentication.

    silent: Whether or not to print errors to the console. Default is False.

    fragile: Whether or not the API should throw an exception if an error occurs (will raise for anything that isn't HTTP200). Default is False
    """
    def __init__(self, token: str, silent: bool = False, fragile: bool = False, rate_limit_timeout: int = 0):
        self.silent = silent
        self.fragile = fragile
        self.rate_limit_timeout = rate_limit_timeout
        self.user: User = User(token)
        
        if not self._validate_token(token):
            print("[!] INVALID TOKEN")
            if self.fragile:
                raise Exception("Invalid token input")
            exit(1)
        
    def get_user_guilds(self) -> list[Guild]:
        """Gets all guilds from the user, returns a list of Guild objects, does NOT include DMs"""
        # Get user guilds
        guilds = requests.get("https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": self.user.token})
        if guilds.status_code == 429:
            if not self.silent:
                print("[!] Getting rate-limited, sleeping for a while... (get_user_guilds())")
            sleep(self.rate_limit_timeout)
            return self.get_user_guilds()
        if guilds.status_code != 200:
            if not self.silent:
                print("[!] Failed to get guilds, status code: " + str(guilds.status_code))
            if self.fragile:
                raise Exception("Failed to get guilds, status code: " + str(guilds.status_code))
            return []
        guilds = guilds.json()

        # Format guilds into a list of Guild objects and return
        guilds_list = [Guild(guild["id"], guild["name"]) for guild in guilds]
        return guilds_list
    
    def get_guild_channels(self, guild: Guild) -> list[Channel]:
        """Gets all channels from a guild, returns a list of Channel objects. 
        
        Note that it also includes channels you are not supposed to see, they will HTTP403 if you try to access them"""
        # Get guild channels
        channels = requests.get(f"https://discord.com/api/v9/guilds/{guild.id}/channels", headers={"Authorization": self.user.token})
        if channels.status_code == 429:
            if not self.silent:
                print("[!] Getting rate-limited, sleeping for a while... (get_guild_channels())")
            sleep(self.rate_limit_timeout)
            return self.get_guild_channels(guild)
        if channels.status_code != 200:
            if not self.silent:
                print("[!] Failed to get channels, status code: " + str(channels.status_code))
            if self.fragile:
                raise Exception("Failed to get channels, status code: " + str(channels.status_code))
            return []
        channels = channels.json()

        # Format channels into a list of Channel objects and return
        channels_list = [Channel(channel["id"], channel["name"]) for channel in channels]
        return channels_list

    def get_channel_messages(self, channel: Channel) -> list[Message]:
        """
        Gets messages from a channel, returns a list of Message objects, from newest to oldest.
        
        Running this on a VC-channel will get the messages from the VC chat.

        Running this on a channel you do not have permissions to will return an empty list (HTTP403)
        """
        # Get channel messages
        messages = requests.get(f"https://discord.com/api/v9/channels/{channel.id}/messages", headers={"Authorization": self.user.token})
        if messages.status_code == 429:
            if not self.silent:
                print("[!] Getting rate-limited, sleeping for a while... (get_channel_messages())")
            sleep(self.rate_limit_timeout)
            return self.get_channel_messages(channel)
        if messages.status_code != 200:
            if not self.silent:
                print(f"[!] Failed to get messages from channel '{channel.name}', status code: " + str(messages.status_code))
            if self.fragile:
                raise Exception(f"Failed to get messages from channel '{channel.name}', status code: " + str(messages.status_code))
            return []
        messages = messages.json()

        # Format messages into a list of Message objects and return
        messages_list = [Message(message["id"], message["author"]["username"], message["author"]["id"], message["content"], message["timestamp"]) for message in messages]
        return messages_list

    def send_message(self, channel: Channel, message: str):
        ret = requests.post(f"https://discord.com/api/v9/channels/{channel.id}/messages", headers={"Authorization": self.user.token}, json={"content": message})
        if ret.status_code == 429:
            if not self.silent:
                print("[!] Getting rate-limited, sleeping for a while... (send_message())")
            sleep(self.rate_limit_timeout)
            self.send_message(channel, message)
            return
        if ret.status_code != 200:
            if not self.silent:
                print(f"[!] Failed to send message to channel '{channel.name}', status code: " + str(ret.status_code))
            if self.fragile:
                raise Exception(f"Failed to send message to channel '{channel.name}', status code: " + str(ret.status_code))

    def _validate_token(self, token: str) -> bool:
        """Validates a token, returns TRUE/FALSE for whether or not a token is valid"""
        test = requests.get("https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": token})
        if test.status_code == 200:
            return True
        elif test.status_code == 403 or test.status_code == 401:
            return False
        else:
            if self.fragile:
                raise Exception(f"Token validation got an unknown response (HTTP{test.status_code})")
            print(f"Token validation got an unknown response (HTTP{test.status_code})")
            return True