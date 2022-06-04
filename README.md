## Docker

- Run `docker-compose -f docker-compose.yml up --build`

## Python

### Interactive Python interpreter

> Type `python3` in the terminal to start the prompt of the interactive Python interpreter

### VS Code Setup

- Select a Python interpreter (lower left)
- Run `*.py` file with start button top right
- F5 to start debugger

### Virtual environment and package installation

- Create and activate the virtual environment:
  - Create: `python3 -m venv .venv`
  - Activate: `source .venv/bin/activate`
- Select your new environment by using the Python: Select Interpreter command from the Command Palette.
- Install packages: `python3 -m pip install <PACKAGE_NAME>`
- Use `pip list` to check which package are installed including information about the version
- Once you are finished, type `deactivate` in the terminal window to deactivate the virtual environment.
