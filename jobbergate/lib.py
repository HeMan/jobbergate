import importlib
import os
import sys
import yaml

jobbergatepath = os.getenv("JOBBERGATE_PATH", "./")

try:
    with open(f"{jobbergatepath}/jobbergate.yaml") as ymlfile:
        jobbergateconfig = yaml.safe_load(ymlfile)
except FileNotFoundError as err:
    print(err)
    sys.exit(1)


def fullpath_import(path, lib):
    """Imports a file from absolute path."""
    if lib in sys.modules:
        del sys.modules[lib]
    sys.path.append(f"{jobbergateconfig['apps']['path']}/{path}/")
    try:
        module = importlib.import_module(lib)
    finally:
        sys.path.remove(f"{jobbergateconfig['apps']['path']}/{path}/")
    return module
