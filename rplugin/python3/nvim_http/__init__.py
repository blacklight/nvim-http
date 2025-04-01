import traceback as tb
from typing import List, Optional

import requests
import pynvim

from .env import get_environment
from .log import Logger
from .parser import parse_http_request, select_surrounding_http_request
from .response import show_http_response


@pynvim.plugin
class HttpRunner:
    """
    A Neovim plugin for running HTTP requests.
    """

    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim
        self.logger = Logger(nvim)
        self._session: Optional[requests.Session] = None

    def _http_run(self, request: dict, vertical: bool = True):
        """
        Run an HTTP request and display the response in a new buffer.
        """
        self.logger.info(f"Running HTTP request: {request['method']} {request['url']}")

        try:
            method = getattr(requests, request.pop("method"))
            url = request.pop("url")
            req_args = {"headers": request.pop("headers", {})}
            if request["payload"].strip():
                req_args["data"] = request["payload"]

            with requests.Session() as self._session:
                rs = method(url, **req_args)

            show_http_response(rs, nvim=self.nvim, vertical=vertical)
        except Exception as e:
            self.logger.error(f"Error running HTTP request: {e}\n\n{tb.format_exc()}")

    @pynvim.command(
        "Http", nargs="?", sync=False, complete="customlist,HttpCommandComplete"
    )
    def http_run(self, args: List[str]):
        """
        Run the HTTP request under the cursor.

        :param vertical: Whether the response should be shown in a vertical buffer.
        """
        vertical = not args or args[0] != "-h"
        mode = self.nvim.call("mode")
        visual = mode in {"v", "V", "q", "Q"}
        text = (
            "\n".join(self.nvim.current.line)  # if normal
            if visual
            else select_surrounding_http_request(self.nvim)
        )

        env = get_environment(self.nvim)
        request = parse_http_request(text, **env)
        self.http_stop()
        self._http_run(request, vertical=vertical)

    @pynvim.command("HttpStop", nargs="*", sync=True)
    def http_stop(self, *_: str):
        """
        Stop the current HTTP request, if it's running.
        """
        if self._session:
            self._session.close()
            self.logger.warning("HTTP request stopped\n")

    @pynvim.function("HttpCommandComplete", sync=True)
    def http_command_complete(self, _: List[str]):
        """
        Return the completion options for the `:Http` command.
        """
        return ["-v", "-h"]
