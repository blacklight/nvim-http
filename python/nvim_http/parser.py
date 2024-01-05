import re

import vim

from .env import env_parse

comment_regex = re.compile(r"^\s*#.*$")
request_head_regex = re.compile(r"^\s*([A-Za-z]+)\s+(.*)(\s+(HTTP/\d\.\d)\s*)?")
request_header_regex = re.compile(r"^\s*([A-Za-z0-9-_]+)\s*:\s*(.*)\s*$")
request_sep_regex = re.compile(r"^\s*###")


def parse_http_request(text: str, **env) -> dict:
    """
    Parse an HTTP request given as a string.
    """
    request = {"headers": {}, "payload": ""}
    parsing_headers = True
    lines = [line for line in text.strip().split("\n") if not comment_regex.match(line)]

    for i, line in enumerate(lines):
        if i == 0:
            m = request_head_regex.match(line)
            assert m, f"Unable to parse the request line: {line}"
            request["method"] = m.group(1).lower()
            request["url"] = env_parse(m.group(2), **env)
        elif not line.strip():
            if parsing_headers:
                parsing_headers = False
        elif parsing_headers:
            line = line.strip()
            m = request_header_regex.match(line)
            assert m, f"Invalid header line: {line}"
            header_name = env_parse(m.group(1), **env)
            request["headers"][header_name] = env_parse(m.group(2), **env)
        else:
            if request["payload"]:
                request["payload"] += "\n"
            request["payload"] += line

    return request


def select_surrounding_http_request() -> str:
    """
    Find the boundaries of the current HTTP request and return the full request
    as a string.
    """
    cursor_orig = vim.current.window.cursor[:]
    vim.current.window.cursor = (vim.current.window.cursor[0], 0)
    request_start_idx = request_end_idx = None

    # Search backwards for the head of the request
    while vim.current.window.cursor[0] >= 0 and request_start_idx is None:
        m = request_head_regex.match(vim.current.line)
        if m:
            request_start_idx = vim.current.window.cursor[0]
        else:
            vim.current.window.cursor = (vim.current.window.cursor[0] - 1, 0)

    if request_start_idx is None:
        vim.current.window.cursor = cursor_orig[:]
        raise AssertionError("Could not find the beginning of this request\n")

    # Search forward for the tail of the request
    while (
        vim.current.window.cursor[0] < len(vim.current.buffer)
        and request_end_idx is None
    ):
        m = request_sep_regex.search(vim.current.line)
        if m:
            vim.current.window.cursor = (max(0, vim.current.window.cursor[0] - 1), 0)
            request_end_idx = vim.current.window.cursor[0]
        else:
            vim.current.window.cursor = (vim.current.window.cursor[0] + 1, 0)

    if request_end_idx is None:
        request_end_idx = len(vim.current.buffer) - 1

    return "\n".join(vim.current.buffer.range(request_start_idx, request_end_idx))
