# Periodic File Auto Transfer
A software capable of periodicly tranfer files from a source folder to a destination folder based on regular expression matches of files.

# Features

- Move files from source dir to destination based on matched regex patterns
- Source and Destination are configurable
- Regex matching is customizable
- Time period maybe entered in seconds, minutes or hours

# Requirements

- Python >= 3.7 (with pip)
- Qt5

# How to Run Source Code

First clone the repository into the desired location. It's recomended to setup an virtual enviroment to run the application. With python installed and inside the cloned directory (active your virtual env, if it exists) run:

```
pip install pyqt5
pip install pyqtgraph
```

After pip fishes the install, just run:

```
cd src
python main.py
```