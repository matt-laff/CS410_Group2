# CS410_Group2
CS 410 Group 2

# TO RUN PROGRAM:
python -m src

# PYTEST RUN COMMAND:
pytest




===================

# Environment Setup
# Windows
pip install virtualenv

right click start menu -> System -> Advanced settings -> Environment Variables
System Variables -> edit PATH -> add path to Python<version #>/Scripts folder to PATH

(in terminal - I have the venv in the directory above the project folder) virtualenv venv 

venv/Scripts/activate

pip install -r requirements.txt

# Mac
pipx install virtualenv

virtualenv venv

source venv/bin/activate

pip install -r requirements


# OS independant
Now you can just run the appropriate activate script and everything should work
