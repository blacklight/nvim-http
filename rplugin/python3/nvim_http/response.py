from http.client import responses
import json
import os
import tempfile

from pynvim import Nvim
from .opts import HttpRequestOptions

response_bufname = os.path.join(tempfile.gettempdir(), "response.http")


def get_http_response_buf(nvim: Nvim):
    """
    Get the buffer object of the HTTP response.
    """
    response_bufs = [buf for buf in nvim.buffers if buf.name == response_bufname]
    return response_bufs[0] if response_bufs else None


def show_http_response(response, nvim: Nvim, opts: HttpRequestOptions):
    """
    Display the response on the given response buffer.

    :param response: The response buffer.
    :param vertical: Whether to display the response in a vertical or horizontal
        buffer.
    """
    buf = get_http_response_buf(nvim)
    cmd = opts.response_buffer_mode.value
    if not buf:
        nvim.command(f"{cmd} {response_bufname}")
        buf = get_http_response_buf(nvim)
        assert buf, "Could not find response buffer"

    try:
        content = json.dumps(response.json(), indent=2)
        buf.options["ft"] = "http"
    except (TypeError, ValueError):
        content = response.text

    print(f"The HTTP request ran in {response.elapsed.total_seconds()} seconds")
    content = (
        f'HTTP/{".".join(list(str(response.raw.version)))} '
        f"{response.status_code} {responses[response.status_code]}\n"
        + "\n".join([f"{name}: {value}" for name, value in response.headers.items()])
        + f'\n\n{content or ""}'
    )

    buf[:] = content.split("\n")
