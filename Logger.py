class Logger:
    """The Logger class is used to log/debug things."""
    def __init__(self, enabled: bool = True):
        """If disabled, print statements and other logging commands won't do anything when executed."""
        self.enabled = enabled

    def print(self, string: str):
        """Prints the given string to the console."""
        if self.enabled:
            print(string)