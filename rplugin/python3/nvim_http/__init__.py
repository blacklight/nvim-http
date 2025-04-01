import traceback as tb
from typing import List, Optional

import requests
import pynvim

from .env import get_environment
from .log import Logger
from .opts import HttpRequestOptions
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

    def _http_run(self, request: dict, opts: HttpRequestOptions):
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
            if opts.timeout:
                req_args["timeout"] = opts.timeout

            with requests.Session() as self._session:
                rs = method(url, **req_args)

            self.logger.debug(f"HTTP response: {rs.status_code} {rs.reason}")
            show_http_response(rs, nvim=self.nvim, opts=opts)
        except Exception as e:
            self.logger.error(f"Error running HTTP request: {e}\n\n{tb.format_exc()}")
        finally:
            self._session = None

    @pynvim.command(
        "Http", nargs="?", sync=False, complete="customlist,HttpCommandComplete"
    )
    def http_run(self, args: List[str]):
        """
        Run the HTTP request under the cursor.

        Args:

            -v / --vertical: Display the response in a vertical split (default)
            -h / --horizontal: Display the response in a horizontal
            -t / --tab: Display the response in a new tab
            -T / --timeout: Set the timeout for the HTTP request, in seconds (default: 10)

        """
        opts = HttpRequestOptions(*args)
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
        self._http_run(request, opts)

    @pynvim.command("HttpStop", nargs="*", sync=True)
    def http_stop(self, *_: str):
        """
        Stop the current HTTP request, if it's running.
        """
        if self._session:
            self._session.close()
            self.logger.warning("HTTP request stopped\n")
            self._session = None

    @pynvim.function("HttpCommandComplete", sync=True)
    def http_command_complete(self, args: List[str]) -> List[str]:
        """
        Return the completion options for the `:Http` command.
        """
        opts = {
            "-v",
            "-h",
            "-t",
            "-T",
            "--vertical",
            "--horizontal",
            "--tab",
            "--timeout",
        }

        if "-v" in args or "--vertical" in args:
            opts.remove("-v")
            opts.remove("--vertical")

        if "-h" in args or "--horizontal" in args:
            opts.remove("-h")
            opts.remove("--horizontal")

        if "-t" in args or "--tab" in args:
            opts.remove("-t")
            opts.remove("--tab")

        if "-T" in args or "--timeout" in args:
            opts.remove("-T")
            opts.remove("--timeout")

        if args and (args[-1] == "-T" or args[-1] == "--timeout"):
            # Return a dummy value to indicate that the next argument should be
            # a number
            return ["10"]

        return list(opts)
