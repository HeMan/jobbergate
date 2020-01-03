import importlib
import sys
import yaml

with open("jobbergate.yaml") as ymlfile:
    config = yaml.safe_load(ymlfile)


def fullpath_import(path, lib):
    """Imports a file from absolute path."""
    if lib in sys.modules:
        del sys.modules[lib]
    sys.path.append(f"{config['apps']['path']}/{path}/")
    try:
        module = importlib.import_module(lib)
    finally:
        sys.path.remove(f"{config['apps']['path']}/{path}/")
    return module
