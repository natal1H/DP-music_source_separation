# Music Separator Application

## Prerequisites:

- python >=3.8
- pip
- virtualenv

If any of them are not present in your system, install them using the following commands:
```
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv
```

## Installation

Move into the directory with the application code and run the `install.sh` or execute the following commands in order:
```
python3 -m venv musicSeparatorEnv
source musicSeparatorEnv/bin/activate
python3 -m pip install -r requirements_app.txt
```
## Launch

To launch the application, run the `run.sh` or:
```
source musicSeparatorEnv/bin/activate
python3 main.py
```