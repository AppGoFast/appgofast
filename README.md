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
   

5. Install **dotnet-trace**: ```dotnet tool install --global dotnet-trace```

6. Run it with: ```python AppGoFast.py```

   If it fails (It shouldn't on Windows) you may need to install tkdnd on your OS. Fedora: ```sudo dnf install tkdnd```
   
## Building into an executable:

1. Complete the steps in section above and verify that the script functions. Make sure you are using the venv.

2. Get the install location of CustomTkinter with: ```python -m pip show customtkinter```

3. Run: ```pyinstaller --noconfirm --onedir --windowed --add-data "<CustomTkinter Location>/customtkinter;customtkinter/" --add-data "<Path to config.json.example>;." --add-data "<Path to profiler_processing/pattern.xml>;profiler_processing/" "<Path to AppGoFast.py>"```

