import json

CONFIG_FILE = "config.json"

DEFAULT_CONFIGS: dict[str, str|bool|int] = {
    "error_silent": False,
    "info_silent": False,
    "action_silent": False,
    "status_silent": False,
    "fragile": False,
    "database_name": "main.sqlite",
    "gather_messages": True,
    "looping_enable": True,
    "looping_timeout": 0,
    "looping_times": 0,
    "targeted_enable": False,
    "targeted_channel_file": "data/channels.txt",
    "notifs_enable": False,
    "notifs_channel": 0,
    "notifs_frequency": 0,
    "channel_culling_enable": True,
    "channel_culling_range": 604800,
    "channel_culling_cache": True,
    "rate_limit_timeout": 600
}

def load_configs() -> dict[str, str|bool|int]:
    # Load in default config if doesnt exist
    try:
        open(CONFIG_FILE, "r").close()
    except FileNotFoundError:
        with open(CONFIG_FILE, "w") as file:
            json.dump(DEFAULT_CONFIGS, file, indent=4)

    # Load configs
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)