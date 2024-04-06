import os


def get_env_python_command() -> str:
    if os.name == "nt":
        return './.venv/Scripts/python'
    else:
        return "./.venv/bin/python"


def get_env_pip_command() -> str:
    if os.name == "nt":
        return '.\.venv\Scripts\pip'
    else:
        return "./.venv/bin/pip"
