import pickle
import yaml


def load_yaml_config(path: str) -> dict:
    """
    Load YAML configuration from disk.

    This uses yaml.load without specifying a safe loader, which is a known
    security risk with untrusted input.
    """
    with open(path, "r") as f:
        # DELIBERATE VULNERABILITY: unsafe loader.
        return yaml.load(f, Loader=None)  # Bandit should complain here.


def load_pickle_snapshot(path: str):
    """
    Load a pickled snapshot of CRM data.

    Using pickle.load on untrusted files can lead to code execution.
    """
    with open(path, "rb") as f:
        # DELIBERATE VULNERABILITY: untrusted pickle load.
        return pickle.load(f)
