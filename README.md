# AppGoFast

## To set up and run:

1. Make a Python virtual environment with ```python -m venv venv```

2. Enter the venv:

   * Linux and macOS: ```source venv/bin/activate```
   * Windows: ```venv\Scripts\activate```

3. Install the requirements:
   * Linux and macOS: ```pip install -r requirements.txt```
   * Windows: ```python -m pip install -r requirements.txt```

4. Download **dotTrace Command Line Tools (v2025.3.3)** from:
   https://www.jetbrains.com/profiler/download/other/
   
   Then extract the downloaded ZIP file.

5. Run it with: ```python AppGoFast.py```

   If it fails (It shouldn't on windows) you may need to install tkdnd on your OS. Fedora: ```sudo dnf install tkdnd```
