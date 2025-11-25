# Releases

This folder contains the compiled executable for the Claude Code Installation Wizard.

## Files

- **Claude Code Setup.exe** - The main installer executable

## Usage

1. Download `Claude Code Setup.exe`
2. Right-click and select "Run as administrator"
3. Follow the installation wizard

## Building from Source

To compile the Python script into an executable:

```bash
pip install pyinstaller
pyinstaller --onefile --name "Claude Code Setup" claude_setup_wizard.py
```

The compiled executable will be created in the `dist` folder and should be moved here for distribution.
