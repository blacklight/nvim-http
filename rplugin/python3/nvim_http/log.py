import logging

import pynvim

pynvim.setup_logging("http_runner")
logger = logging.getLogger(__name__)


class Logger:
    """
    A logger adapter that writes to the Neovim output.
    """

    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    def debug(self, msg: str):
        logger.debug(msg)

    def info(self, msg: str):
        logger.info(msg)
        self.nvim.out_write(f"{msg}\n")

    def warning(self, msg: str):
        logger.warning(msg)
        self.nvim.err_write(f"{msg}\n")

    def error(self, msg: str):
        logger.error(msg)
        self.nvim.err_write(f"{msg}\n")
