#!/usr/bin/env python3

import os
import sys
import importlib
from platform import system as detsys
from enum import Enum
from typing import NoReturn, List

# NOTES:
# run build tool with python's -OO argument
# to build the true release, otherwise
# debug mode

class TryImportError(ImportError):
    pass

class PlatformNotSupportedError(Exception):
    pass

class Configuration(Enum):
    TARGET_SCRIPT="HeaderGen.py"
    OUT_NAME="HeaderGen"
    LOG_LEVEL="ERROR"
    ICON_IMG: str=None

    @classmethod
    def get(cls, attrib: str) -> object:
        return cls.__dict__[attrib].value

def tryimpbuildmod(toplevel_module: str, subofmodule: str = ".") -> object:
    try:
        mod = importlib.import_module(subofmodule, toplevel_module)
        return mod
    except ImportError:# or ModuleNotFoundError: -- modulenotfounderror is just a subset of importerror...
                        # also dont wanna cause errors on earlier versions than 3.6...
        raise TryImportError("Failed to import module: {}{}".format(toplevel_module,subofmodule))

def gen_options(platform: str) -> List[str]:
    options: List[str] = []
    if (platform == "windows" or platform == "linux"):
        # universal opts for these two platforms
        options.append(Configuration.get("TARGET_SCRIPT"))
        options.append("-n={}".format(Configuration.get("OUT_NAME")))
        options.append("-y")
        options.append("--clean")
        options.append("--onefile")
        options.append("--log-level={}".format(Configuration.get("LOG_LEVEL")))
        if (platform == "windows" and
            Configuration.get("ICON_IMG") != None
        ):
            options.append("-i={}".format(Configuration.get("ICON_IMG")))


    else:
        platform_not_supported(platform)

    return options

def finalize_build(plat: str, bt: object, opts: List[str]) -> None:
    if (plat == "windows" or plat == "linux"):
        # currently only uses pyinstaller...
        bt.run(opts)

def platform_not_supported(plat) -> NoReturn:
    raise PlatformNotSupportedError(
        "Your platform ({}) is currently not supported for pre-built release binaries!".format(
            plat.upper()
        )
    )

def is_supported_sys(plattype: str) -> None or NoReturn:
    if not (plattype == "windows" or plattype == "linux"):
        platform_not_supported(plattype)

def build() -> None or NoReturn:
    systype = detsys().lower()
    is_supported_sys(systype)
    bt: object = tryimpbuildmod("PyInstaller",".__main__")
    build_opts: List[str] = gen_options(systype)
    finalize_build(systype, bt, build_opts)

###
### ENTRY
###

def main() -> None or NoReturn:
    build()
    sys.exit()

if __name__ == "__main__":
    main()
