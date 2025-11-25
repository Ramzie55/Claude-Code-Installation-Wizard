# Claude Code Installation Wizard

A professional Windows installer for Claude Code - Anthropic's official CLI tool.

## Features

- Automated system requirements checking
- Node.js and npm verification
- One-click Claude Code installation
- Automatic PATH configuration
- Desktop shortcut creation
- Beautiful terminal UI with progress tracking
- Comprehensive error handling and logging

## Requirements

- Windows 10/11
- Administrator privileges
- Node.js v16 or higher
- npm package manager

## Installation

### Option 1: Run the Compiled Executable

1. Download `Claude Code Setup.exe` from the [releases](./releases) folder
2. Right-click the executable and select "Run as administrator"
3. Follow the on-screen instructions

### Option 2: Run the Python Script

1. Ensure Python 3.7+ is installed
2. Clone this repository:
   ```bash
   git clone https://github.com/Ramzie55/Claude-Code-Installation-Wizard.git
   cd Claude-Code-Installation-Wizard
   ```
3. Run the installer as administrator:
   ```bash
   python claude_setup_wizard.py
   ```

## What Does It Do?

The installer performs the following steps:

1. **System Requirements Check** - Verifies Windows version, admin rights, and disk space
2. **Node.js Verification** - Confirms Node.js and npm are installed
3. **Claude Code Installation** - Installs or updates Claude Code via npm
4. **PATH Configuration** - Adds Claude Code to system PATH
5. **Installation Verification** - Tests the installation
6. **Desktop Shortcut** - Creates a convenient desktop shortcut
7. **Summary Report** - Displays installation results and next steps

## Usage After Installation

After successful installation:

1. Close the installer window
2. Open a NEW Command Prompt or Terminal
3. Verify installation:
   ```bash
   claude --version
   ```
4. Start using Claude Code:
   ```bash
   claude
   ```

## Logs

Installation logs are saved to:
```
%USERPROFILE%\.claude_setup_logs\
```

## Troubleshooting

### "Administrator privileges required"
Right-click Command Prompt and select "Run as administrator" before running the installer.

### "Node.js not found"
Download and install Node.js from [nodejs.org](https://nodejs.org) before running the installer.

### "claude command not found" after installation
Open a new terminal window. The PATH changes only take effect in new terminal sessions.

## Building the Executable

To compile the Python script into an executable:

```bash
pip install pyinstaller
pyinstaller --onefile --name "Claude Code Setup" --icon=icon.ico claude_setup_wizard.py
```

The executable will be created in the `dist` folder.

## License

MIT License - see [LICENSE](./LICENSE) file for details.

## Author

Created by Ramzie

## Contributing

Contributions, issues, and feature requests are welcome!

## Support

If you encounter any issues, please open an issue on GitHub.
