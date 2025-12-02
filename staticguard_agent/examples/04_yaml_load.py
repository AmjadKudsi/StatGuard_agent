import yaml

def load_config(path):
    # yaml.load without SafeLoader can be unsafe
    with open(path, "r") as f:
        cfg = yaml.load(f)
    return cfg
