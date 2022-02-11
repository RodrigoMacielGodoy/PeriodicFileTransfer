# Periodic File Auto Transfer
A software capable of periodicly tranfer files from a source folder to a destination folder based on regular expression matches of files.

# Features

- Move files from source dir to destination based on matched regex patterns
- Source and Destination are configurable
- Regex matching is customizable
- Time period maybe entered in seconds, minutes or hours
- Data logging available
- Some transfer statistics displayed in charts

# Requirements

- Python >= 3.7 (with pip)

# How to Run Source Code

First clone the repository into the desired location. It's recomended to setup an virtual enviroment to run the application. With PowerShell (Windows) or Terminal (Mac and Linux) go inside the cloned directory (active your virtual env, if it exists) then run:

```
pip install -r install_requirements
```

Or individually install:

```
pip install PyQt5
pip install PyQtChart
```

After fishing the installation, just run:

```
cd src
python main.py
```
