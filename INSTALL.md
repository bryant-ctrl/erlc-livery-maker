# Installation Guide

## System Requirements

- Python 3.8 or newer
- Linux or Windows
- Internet connection (for AI generation)

## Linux Installation

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-tk python3-venv
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip python3-tkinter
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip tk
```

### 2. Install Python Dependencies

```bash
cd "ERLC Livery Maker"
pip3 install -r requirements.txt
```

### 3. Run the Application

```bash
./run.sh
# Or directly:
python3 src/main_tk.py
```

## Windows Installation

### 1. Install Python

Download and install Python from https://www.python.org/downloads/

**Important:** Check "Add Python to PATH" during installation

Tkinter is included with the standard Windows Python installation.

### 2. Install Python Dependencies

Open Command Prompt or PowerShell:
```cmd
cd "ERLC Livery Maker"
pip install -r requirements.txt
```

### 3. Run the Application

Double-click `run.bat` or run:
```cmd
python src\main_tk.py
```

## Building Executables

### AppImage (Linux)

**Requirements:**
- All system dependencies installed
- wget (for downloading appimagetool)

```bash
./build_appimage.sh
```

The AppImage will be created as `ERLC_Livery_Maker-x86_64.AppImage`

**Note:** python3-tk must be installed on the build system for the AppImage to include Tkinter.

### Windows .exe

**Requirements:**
- Python and pip installed
- PyInstaller

```bash
pip install pyinstaller
pyinstaller build_windows.spec
```

The executable will be in `dist/ERLC_Livery_Maker.exe`

## Troubleshooting

### "No module named 'tkinter'"

**Linux:**
```bash
sudo apt-get install python3-tk   # Ubuntu/Debian
sudo dnf install python3-tkinter   # Fedora
sudo pacman -S tk                  # Arch
```

**Windows:**
Tkinter should be included. If missing, reinstall Python from python.org

### "No module named 'PIL'" or other missing modules

```bash
pip install -r requirements.txt
```

### AppImage won't run

1. Make it executable: `chmod +x ERLC_Livery_Maker-x86_64.AppImage`
2. Try running from terminal to see error messages
3. Ensure python3-tk was installed when building

### Windows .exe shows console window

This is normal. The window will appear when the app starts.

## Getting Your Replicate API Key

1. Go to https://replicate.com/
2. Sign up for a free account
3. Navigate to Account Settings
4. Copy your API token
5. Paste it into the app's API Configuration section

## Next Steps

See [QUICKSTART.md](QUICKSTART.md) for usage instructions.
