import importlib
import sys
import yaml

with open("jobbergate.yaml") as ymlfile:
    config = yaml.safe_load(ymlfile)


def fullpath_import(path, lib):
    """Imports a file from absolute path."""
    old_syspath = sys.path
    sys.path.append(f"{config['apps']['path']}/{path}/")
    module = importlib.import_module(lib)
    sys.path = old_syspath

    return module
