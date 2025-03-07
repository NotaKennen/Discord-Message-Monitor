"""
print("\033[31mThis is red font.\033[0m")
print("\033[32mThis is green font.\033[0m")
print("\033[33mThis is yellow font.\033[0m")
print("\033[34mThis is blue font.\033[0m")
print("\033[37mThis is the default font.\033[0m")
"""

class Logservice:
    def __init__(self, i_silent: bool = False, a_silent: bool = False, e_silent: bool = False, s_silent: bool = False):
        self.modes: dict[str, str] = {
                "info": "\033[34m[?]",
                "action": "\033[33m[*]",
                "error": "\033[31m[!]",
                "status": "\033[37m[-]"
            }
        
        self.INFO_SILENT = i_silent
        self.ACTION_SILENT = a_silent
        self.ERROR_SILENT = e_silent
        self.STATUS_SILENT = s_silent

    def log(self, message: str, level: str = "info"):
        level = level.lower()
        if level not in self.modes:
            raise Exception(f"'{level}' is not a defined log level")

        # TODO: figure out a better mechanism for disabling action levels
        if self.INFO_SILENT and level == "info":
            return
        if self.ACTION_SILENT and level == "action":
            return
        if self.ERROR_SILENT and level == "error":
            return
        if self.STATUS_SILENT and level == "status":
            return

        print(f"{self.modes[level]} {message}\033[0m")

GLOBAL_LOGSERVICE = Logservice()