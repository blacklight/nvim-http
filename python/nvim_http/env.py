import json
import os
import re
import sys

import vim

env_file_regex = re.compile(r".*\.?env\.json$")
env_var_regex = re.compile(r"{{([A-Za-z0-9-_]+)}}")


def env_parse(text: str, **env) -> str:
    """
    Try and parse a string of text from the environment and replace it with the
    corresponding variable value, or it leaves it unchanged if no matching
    variables exist.
    """
    return env_var_regex.sub(
        lambda m: env.get(m.group(1), "{{" + m.group(1) + "}}"), text
    )


def get_environments() -> dict:
    """
    Load all the available environments from the `./*.env.json` files.
    """
    envs = {}
    curfile = vim.eval('expand("%")')
    dirs = {
        os.path.abspath("."),
        os.path.abspath(os.path.dirname(curfile)),
    }

    env_files = [
        os.path.join(d, f)
        for d in dirs
        for f in os.listdir(d)
        if os.path.isdir(d) and env_file_regex.match(f)
    ]

    for env_file in env_files:
        try:
            with open(env_file) as f:
                envs.update(json.load(f))
        except Exception:
            pass

    return envs


def get_environment() -> dict:
    """
    Prompt the user for an environment and return it as a dictionary.
    """
    envs = get_environments()
    if not envs:
        return {}
    if len(envs) == 1:
        return list(envs.values())[0]

    env_names = list(envs.keys())
    envs = list(envs.values())
    env_idx = vim.eval(
        'input("Select an environment\\n\\n'
        + "\\n".join([f"{i+1}: {name}" for i, name in enumerate(env_names)])
        + '\\n\\n> ")'
    )

    try:
        env_idx = int(env_idx) - 1
        assert 0 <= env_idx < len(envs), "Invalid index"
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        return {}

    return envs[env_idx]
