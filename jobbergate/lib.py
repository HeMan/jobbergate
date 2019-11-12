import importlib
import yaml

with open("jobbergate.yaml") as ymlfile:
    config = yaml.safe_load(ymlfile)


def fullpath_import(path, lib):
    app_path = f"{config['apps']['path']}/{path}/{lib}.py"
    spec = importlib.util.spec_from_file_location(".", app_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
