import logging
from typing import Optional

import pynvim

pynvim.setup_logging("http_runner")


class Logger:
    """
    A logger adapter that writes to the Neovim output.
    """

    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim
        self._logger = logging.getLogger(__name__)

    def debug(self, msg: str):
        self._logger.debug(msg)

    def info(self, msg: str):
        self._logger.info(msg)
        self.nvim.out_write(f"{msg}\n")

    def warning(self, msg: str):
        self._logger.warning(msg)
        self.nvim.err_write(f"{msg}\n")

    def error(self, msg: str):
        self._logger.error(msg)
        self.nvim.err_write(f"{msg}\n")


_logger: Optional[Logger] = None


def set_logger(nvim: pynvim.Nvim):
    global _logger

    if _logger is None:
        _logger = Logger(nvim)

    return _logger


def logger() -> Logger:
    if _logger is None:
        raise ValueError("Logger not set")
    return _logger
