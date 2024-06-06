from dataclasses import dataclass
import multiprocessing
import sys
from typing import Optional

import requests

import vim

from .env import get_environment
from .parser import parse_http_request, select_surrounding_http_request
from .response import show_http_response


@dataclass
class CurrentRequest:
    """
    A simple wrapper for the current request process singleton.
    """

    proc: Optional[multiprocessing.Process] = None

    def clear(self):
        self.proc = None


current_request = CurrentRequest()
result_queue = multiprocessing.Queue()


def _run_http_request(request: dict, vertical: bool = True):
    """
    Run an HTTP request and display the response in a new buffer.
    """
    try:
        method = getattr(requests, request.pop("method"))
        url = request.pop("url")
        req_args = {"headers": request.pop("headers", {})}
        if request["payload"].strip():
            req_args["data"] = request["payload"]

        rs = method(url, **req_args)

        show_http_response(rs, vertical=vertical)
        result_queue.put(rs)
    except Exception as e:
        result_queue.put(e)
    finally:
        current_request.clear()


def http_run(vertical: bool = True):
    """
    Run the HTTP request under the cursor.

    :param vertical: Whether the response should be shown in a vertical buffer.
    """
    mode = vim.call("mode")
    visual = mode in {"v", "V", "q", "Q"}
    text = "\n".join(vim.current.range) if visual else select_surrounding_http_request()
    env = get_environment()
    request = parse_http_request(text, **env)
    http_stop()

    def _run():
        print("Running HTTP request")
        current_request.proc = multiprocessing.Process(
            target=_run_http_request, args=(request,), kwargs={"vertical": vertical}
        )
        current_request.proc.start()

    vim.async_call(_run)


def http_stop():
    """
    Stop the current HTTP request, if it's running.
    """
    if current_request.proc:
        current_request.proc.kill()
        result_queue.put(InterruptedError("The request was terminated"))
        current_request.clear()
