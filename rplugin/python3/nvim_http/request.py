from dataclasses import dataclass
import multiprocessing
from typing import Optional


@dataclass
class CurrentRequest:
    """
    A simple wrapper for the current request process singleton.
    """

    proc: Optional[multiprocessing.Process] = None

    def clear(self):
        self.proc = None
