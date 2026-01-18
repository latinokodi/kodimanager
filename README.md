# Kodi Manager

A Windows desktop application to manage multiple portable instances of Kodi 64-bit.

## Overview
Kodi Manager allows users to:
- Download Kodi from official sources (or mirrors).
- Install Kodi in "portable mode" to separate folders.
- Maintain multiple independent installations side-by-side.
- Launch instances with the correct `-p` flag.
- "Clean Sweep" instances (reset user data) individually.

## Architecture
The application is built with a clear separation of concerns:
- **Core Logic (`src/kodimanager/core`)**: Handles downloading, extracting, and instance registry management. Independent of the GUI.
- **GUI (`src/kodimanager/gui`)**: A responsive interface built with PyQt6.
- **Data**: Uses a simple JSON `instances.json` to track installed versions and paths.

### Tech Stack
- **Language**: Python 3.10+ (Selected for robust file handling, excellent standard library, and cross-platform support).
- **GUI Framework**: `PyQt6` (Professional, native look and feel, robust event loop).
- **Network**: `requests` + `beautifulsoup4` (Reliable header handling and parsing for download pages).
- **Environment**: Virtual Environment (`venv`) based (Strategy B).

## Use of Filesystem
- **Project Root**: Contains source code and launchers.
- **Runtime Data**: 
    - Configuration and Instance Registry are stored in `%APPDATA%\KodiManager` (Windows) or `~/.config/kodimanager` (Linux) to avoid polluting the workspace, though portable instances can be installed anywhere the user chooses (defaulting to a `KodiInstances` folder).
    - **Note**: The application respects the "External Files" rule by default but allows user overrides.

## Installation & Running

### Prerequisites
- Windows 10/11 (Primary target) or Linux.
- Python 3.10 or higher installed.

### Running
We use **Strategy B: Project-local environment**.

**Windows:**
Double-click `run_app.bat`. This will:
1. Create a Python virtual environment (`venv`) if missing.
2. Install dependencies.
3. Launch the application.

**Linux/macOS:**
Run `./run_app.sh`.

## Testing
Run tests with:
```bash
# Activate venv first
python -m pytest tests
```

## Security & Performance
- Downloads are verified if hashes are available (future improvement).
- No admin privileges required for standard operation (unless installing to protected folders, which is discouraged).
- "Clean Sweep" is a destructive operation; the UI includes confirmation dialogs.
