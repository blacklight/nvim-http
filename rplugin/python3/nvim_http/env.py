import json
import os
import re
import sys

from pynvim import Nvim

env_file_regex = re.compile(r"(.*\.?env\.json)|(\.env)$")
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


def parse_env_json(env_file: str) -> dict:
    """
    Parse environment configuration from a JSON file and return it as a dictionary.
    """
    with open(env_file) as f:
        return json.load(f)


def parse_dot_env(env_file: str) -> dict:
    """
    Parse an environment from a .env file and return it as a dictionary.
    """
    # Try to parse the environment file as a key-value pair file
    env = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            tokens = line.split("=", 1)
            if len(tokens) < 2:
                continue

            env[tokens[0].strip()] = "=".join(tokens[1:]).strip()

    return env


def get_environments(nvim: Nvim) -> dict:
    """
    Load all the available environments from the `./*.env.json` files.
    """
    envs = {}
    curfile = nvim.eval('expand("%")')
    pwd = nvim.eval("getcwd()")
    dirs = {
        pwd,
        os.path.abspath(os.path.dirname(curfile)),
    }

    env_files = [
        os.path.join(d, f)
        for d in dirs
        if os.path.isdir(d)
        for f in os.listdir(d)
        if env_file_regex.match(f)
    ]

    default_env = {}

    for env_file in env_files:
        if env_file.endswith(".env.json"):
            envs.update(parse_env_json(env_file))
        elif env_file.endswith(".env"):
            default_env.update(parse_dot_env(env_file))

    # The default environment is shared across all environments
    if envs:
        for env in envs.values():
            env.update(default_env)
    else:
        envs["default"] = default_env

    return envs


def get_environment(nvim: Nvim) -> dict:
    """
    Prompt the user for an environment and return it as a dictionary.
    """
    envs = get_environments(nvim)
    if not envs:
        return {}
    if len(envs) == 1:
        return list(envs.values())[0]

    env_names = list(envs.keys())
    envs = list(envs.values())
    env_idx = nvim.eval(
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
