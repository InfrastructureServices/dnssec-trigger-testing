class Error(Exception):
    """
    Base class for exceptions in this module
    """
    pass


class ConfigError(Error):
    """
    Error during configuration (e.g. when running ip command)
    """
    def __init__(self, command, arguments, error=None):
        self.command = command
        self.arguments = arguments
        self.error = error

    def __str__(self):
        base = "Configuration error in command: " + self.command + " with args: " + self.arguments
        msg = base + ". Returned: " + self.error if self.error is not None else base
        return msg

    __repr__ = __str__

