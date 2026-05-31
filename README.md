# AppGoFast

## To set up and run:

1. Make a Python virtual environment with ```python -m venv venv```

2. Enter the venv:
   * Windows: ```venv\Scripts\activate```
   * Linux: ```source venv/bin/activate```

3. Install the requirements:
   * Windows: ```python -m pip install -r requirements.txt```
   * Linux: ```pip install -r requirements.txt```

4. Install **dotnet-trace**: ```dotnet tool install --global dotnet-trace```

5. On Windows, download **dotTrace Command Line Tools (v2025.3.3)** from:
   https://www.jetbrains.com/profiler/download/other/
   
   Then extract the downloaded ZIP file.

6. Run it with: ```python AppGoFast.py```

   If it fails you may need to install tkdnd on your OS. Fedora: ```sudo dnf install tkdnd```
   

