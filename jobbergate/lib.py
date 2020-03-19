"""
lib
===

Reads jobbergateconfig and declares functions neede for both web and cli
version.
"""

import importlib
import os
import sys
import yaml

jobbergatepath = os.getenv("JOBBERGATE_PATH", "./")

if os.path.isdir(jobbergatepath):
    try:
        with open(f"{jobbergatepath}/jobbergate.yaml") as ymlfile:
            jobbergateconfig = yaml.safe_load(ymlfile)
    except FileNotFoundError as err:
        if __name__ == "__main__":
            print(err)
            sys.exit(1)
        else:
            jobbergateconfig = {}
else:
    try:
        app = importlib.import_module(jobbergatepath, package=None)
        path = os.path.join(os.path.dirname(app.__file__), "apps")
        jobbergateconfig = {"apps": {"path": path}}
    except ModuleNotFoundError as err:
        print(err)
        jobbergateconfig = {}
        sys.exit(1)


def fullpath_import(path, lib):
    """Imports a file from absolute path.

    :param path: full path to lib
    :param lib: lib to import
    """
    if lib in sys.modules:
        del sys.modules[lib]
    sys.path.append(f"{jobbergateconfig['apps']['path']}/{path}/")
    try:
        module = importlib.import_module(lib)
    finally:
        sys.path.remove(f"{jobbergateconfig['apps']['path']}/{path}/")
    return module
