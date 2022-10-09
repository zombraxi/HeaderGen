# HeaderGen

A Scriptable C/C++ Header File Generator

## Usage

HeaderGen is meant to be run with arguments.
Something to note is, without running the Python interpreter with `-OO`, the script will run in `DEVELOPMENT MODE` and output `DEBUG LOGS`.

### Arguments

1. `--help` (or no arguments) - Displays a help menu.
2. `--new [opt: file]` - Creates a templated HeaderGen script, with the optional choice of including a custom name for the script.
3. `--run [required: file]` - Runs the HeaderGen script "file"

## Build Frozen Executable

In order to build the frozen executable, ensure that you have PyInstaller module installed via PIP, and proceed to run `build_release.py` with `-OO` option for a `RELEASE_MODE` build like so...
```
python3 -OO build_release.py
```
or...
```
python -OO build_release.py
```
Then you will have an outputted frozen executable in the `dist` folder. Feel free to the delete `build` folder.
