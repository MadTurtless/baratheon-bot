import logging
import sys

class BotLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - [%(levelname)s]%(file_info)s - %(message)s",
            handlers=[
                logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
                logging.StreamHandler(stream=sys.stdout)
            ]
        )

    def _get_caller_info(self):
        """Helper to grab the filename and line number of the caller."""
        try:
            # frame 0 is this function, frame 1 is 'error()', frame 2 is the actual bot code
            frame = sys._getframe(2)
            filename = frame.f_code.co_filename.split('/')[-1]  # Just the short filename
            lineno = frame.f_lineno
            return f" - ({filename}:{lineno})"
        except Exception:
            return ""

    def info(self, msg, *args, **kwargs):
        # Info logs get no file context
        kwargs['extra'] = {'file_info': ''}
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        # Error logs dynamically fetch and format the caller info
        caller_info = self._get_caller_info()
        kwargs['extra'] = {'file_info': caller_info}
        self.logger.error(msg, *args, **kwargs)