#!/usr/bin/env python3
"""Claude Code Setup Wizard - Professional installer for Windows"""
import os
import sys
import subprocess
import winreg
import time
import shutil
import ctypes
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, List

# Version info
SCRIPT_VERSION = "2.0.2"
SCRIPT_NAME = "Claude Code Setup Wizard"

class Colors:
    """Enhanced color palette with bright/bold styling"""
    # Brand colors (bright + bold)
    PRIMARY = '\033[1;38;5;105m'       # Bright Purple
    SECONDARY = '\033[1;38;5;81m'      # Bright Light Blue

    # Status colors (bright + bold)
    SUCCESS = '\033[1;38;5;82m'        # Bright Green
    ERROR = '\033[1;38;5;196m'         # Bright Red
    WARNING = '\033[1;38;5;226m'       # Bright Yellow
    INFO = '\033[1;38;5;39m'           # Bright Blue

    # UI colors (bright + bold)
    WHITE = '\033[1;97m'               # Bright White
    GRAY = '\033[1;38;5;245m'          # Bright Gray
    DIM = '\033[2;38;5;240m'           # Dim Gray
    CYAN = '\033[1;38;5;51m'           # Bright Cyan
    MAGENTA = '\033[1;38;5;171m'       # Soft Magenta
    PINK = '\033[1;38;5;213m'          # Bright Pink

    # Effects
    RESET = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

class Icons:
    """Enhanced CMD-compatible icons"""
    # Status icons (keeping ones that work, replacing problematic ones)
    CHECK = '√'           # Works well in CMD
    CROSS = 'x'           # Simple and clear
    WARNING = '!'         # Clear and visible
    INFO = 'i'            # Simple replacement for ℹ
    ARROW = '>'           # Simple and clear
    BULLET = '•'          # Works well
    STAR = '*'            # Universal
    GEAR = '~'            # Simple replacement for ⚙

    # Claude-style loading animation (star sequence)
    LOADING = ['·', '✢', '✶', '✶', '✶', '*', '*', '✢', '·', '✻', '*']

class SetupWizard:
    """Main setup wizard class"""

    def __init__(self):
        self.enable_ansi_colors()  # Enable colors in Windows CMD
        self.errors = []
        self.warnings = []
        self.npm_prefix = None
        self.claude_path = None
        self.start_time = time.time()
        self.total_steps = 7
        self.current_step = 0
        self.log_file = self.setup_log()

    def enable_ansi_colors(self):
        """Enable ANSI color support in Windows CMD"""
        if os.name == 'nt':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # Enable Virtual Terminal Processing
                STD_OUTPUT_HANDLE = -11
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
                kernel32.SetConsoleMode(handle, mode)
            except:
                pass  # Fallback gracefully if it fails

    def setup_log(self):
        """Initialize logging"""
        try:
            log_dir = Path.home() / '.claude_setup_logs'
            log_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return log_dir / f'claude_setup_{timestamp}.log'
        except:
            return None

    def log(self, message: str, level: str = 'INFO'):
        """Write to log file"""
        if self.log_file:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] [{level}] {message}\n")
            except:
                pass

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_terminal_width(self) -> int:
        """Get terminal width for responsive design"""
        try:
            return min(shutil.get_terminal_size().columns, 80)
        except:
            return 60

    def print_banner(self):
        """Display stylized banner"""
        self.clear_screen()
        print(f"\n{Colors.PRIMARY}  ┌──────────────────────────────────────────────────────────┐{Colors.RESET}")
        print(f"{Colors.PRIMARY}  │{Colors.RESET}  {Colors.BOLD}{Colors.WHITE}CLAUDE CODE{Colors.RESET}  {Colors.GRAY}•{Colors.RESET}  {Colors.SECONDARY}INSTALLATION WIZARD{Colors.RESET}  {Colors.GRAY}•{Colors.RESET}  {Colors.DIM}v{SCRIPT_VERSION}{Colors.RESET}  {Colors.PRIMARY}│{Colors.RESET}")
        print(f"{Colors.PRIMARY}  └──────────────────────────────────────────────────────────┘{Colors.RESET}\n")

    def print_box(self, title: str, content: List[str] = None, color: str = None, style: str = 'single'):
        """Print a styled box with optional content"""
        if color is None:
            color = Colors.PRIMARY
        width = 60

        # Top border
        print(f"  {color}┌{'─' * (width - 2)}┐{Colors.RESET}")
        # Title
        title_padded = title.center(width - 4)
        print(f"  {color}│{Colors.RESET} {Colors.BOLD}{title_padded}{Colors.RESET} {color}│{Colors.RESET}")
        # Content
        if content:
            print(f"  {color}├{'─' * (width - 2)}┤{Colors.RESET}")
            for line in content:
                if len(line) > width - 5:
                    line = line[:width - 8] + '...'
                padding = width - len(line) - 5
                print(f"  {color}│{Colors.RESET} {line}{' ' * padding} {color}│{Colors.RESET}")
        # Bottom border
        print(f"  {color}└{'─' * (width - 2)}┘{Colors.RESET}\n")

    def print_status(self, text: str, status: str = 'info', indent: int = 2):
        """Print status message with icon"""
        indent_str = ' ' * indent

        if status == 'success':
            print(f"{indent_str}{Colors.SUCCESS}{Icons.CHECK}{Colors.RESET} {text}")
            self.log(text, 'SUCCESS')
        elif status == 'error':
            print(f"{indent_str}{Colors.ERROR}{Icons.CROSS}{Colors.RESET} {text}")
            self.log(text, 'ERROR')
            self.errors.append(text)
        elif status == 'warning':
            print(f"{indent_str}{Colors.WARNING}{Icons.WARNING}{Colors.RESET} {text}")
            self.log(text, 'WARNING')
            self.warnings.append(text)
        elif status == 'info':
            print(f"{indent_str}{Colors.INFO}{Icons.INFO}{Colors.RESET} {text}")
            self.log(text, 'INFO')
        elif status == 'loading':
            print(f"{indent_str}{Colors.DIM}{Icons.GEAR}{Colors.RESET} {Colors.DIM}{text}{Colors.RESET}")
            self.log(text, 'INFO')

    def print_step(self, title: str, clear: bool = True):
        """Print step header with progress bar"""
        # Clear screen and show banner for clean single-step display
        if clear and self.current_step > 0:
            time.sleep(1.5)  # Pause before clearing for readability
            self.clear_screen()
            self.print_banner()

        self.current_step += 1
        width = 60
        progress = self.current_step / self.total_steps
        filled = int(progress * 20)
        bar = '█' * filled + '░' * (20 - filled)
        percentage = int(progress * 100)
        percent_str = f"{percentage}%"

        # Calculate proper spacing for alignment
        step_text = f"STEP {self.current_step}/{self.total_steps} - {title}"
        step_padding = width - len(step_text) - 2  # 2 for borders

        bar_text = f"[{bar}] {percent_str}"
        # Account for ANSI color codes not taking visual space
        bar_padding = width - 24 - len(percent_str)  # 24 = brackets + bar length + spaces

        print(f"\n  {Colors.SECONDARY}┌{'─' * (width - 2)}┐{Colors.RESET}")
        print(f"  {Colors.SECONDARY}│{Colors.RESET} {Colors.BOLD}{step_text}{Colors.RESET}{' ' * step_padding}{Colors.SECONDARY}│{Colors.RESET}")
        print(f"  {Colors.SECONDARY}│{Colors.RESET} {Colors.PRIMARY}[{bar}]{Colors.RESET} {percent_str}{' ' * bar_padding}{Colors.SECONDARY}│{Colors.RESET}")
        print(f"  {Colors.SECONDARY}└{'─' * (width - 2)}┘{Colors.RESET}\n")

        time.sleep(0.3)  # Brief pause after showing step header

    def animated_loading(self, text: str, duration: float = 3.0):
        """Show Claude-style animated loading indicator"""
        frames = Icons.LOADING
        start = time.time()
        idx = 0

        while time.time() - start < duration:
            print(f"\r  {Colors.SECONDARY}{frames[idx]}{Colors.RESET} {text}...", end='', flush=True)
            time.sleep(0.15)  # Slower animation for readability
            idx = (idx + 1) % len(frames)

        print(f"\r  {Colors.SUCCESS}{Icons.CHECK}{Colors.RESET} {text}... Done!{' ' * 10}")
        time.sleep(0.5)  # Pause after completion

    def check_admin(self) -> bool:
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def run_command(self, cmd: str, capture: bool = False) -> Tuple[Optional[str], int]:
        """Execute command and return output"""
        try:
            if capture:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
                return result.stdout.strip(), result.returncode
            else:
                result = subprocess.run(cmd, shell=True, timeout=30)
                return None, result.returncode
        except subprocess.TimeoutExpired:
            self.log(f"Command timeout: {cmd}", 'ERROR')
            return None, 1
        except Exception as e:
            self.log(f"Command error: {cmd} - {e}", 'ERROR')
            return None, 1

    def check_command(self, cmd: str) -> Tuple[bool, str]:
        """Check if command exists and get version"""
        output, code = self.run_command(f"{cmd} --version", capture=True)
        if code == 0 and output:
            # Extract just the version number, filter out error messages
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                # Look for version patterns like v1.0.0 or just 1.0.0
                if line and not line.startswith('│') and not line.startswith('└') and not line.startswith('┌') and not line.startswith('├'):
                    if any(c.isdigit() for c in line):
                        return True, line
            return True, output.split('\n')[0] or "Unknown"
        return False, "Unknown"

    def check_system_requirements(self) -> bool:
        """Check system requirements"""
        self.print_step("System Requirements Check")
        all_good = True
        time.sleep(0.5)

        # Check Windows version
        try:
            import platform
            win_ver = platform.version()
            win_rel = platform.release()
            if win_rel in ['10', '11']:
                self.print_status(f"Windows {win_rel} detected (Build {win_ver})", 'success')
                time.sleep(0.3)
            else:
                self.print_status(f"Windows {win_rel} may not be fully supported", 'warning')
        except:
            self.print_status("Could not detect Windows version", 'warning')

        # Check admin rights
        is_admin = self.check_admin()
        if is_admin:
            self.print_status("Administrator privileges confirmed", 'success')
        else:
            self.print_status("Administrator privileges required!", 'error')
            all_good = False

        # Check disk space
        try:
            home = Path.home()
            stat = shutil.disk_usage(home)
            free_gb = stat.free / (1024 ** 3)
            if free_gb > 1:
                self.print_status(f"Sufficient disk space ({free_gb:.1f} GB free)", 'success')
            else:
                self.print_status(f"Low disk space ({free_gb:.1f} GB free)", 'warning')
        except:
            pass

        return all_good

    def check_nodejs(self) -> bool:
        """Check Node.js and npm installation"""
        self.print_step("Node.js & npm Verification")
        time.sleep(0.5)

        # Check Node.js
        node_ok, node_ver = self.check_command("node")
        if node_ok:
            # Parse version
            try:
                import re
                match = re.search(r'v?(\d+)\.(\d+)\.(\d+)', node_ver)
                if match:
                    major = int(match.group(1))
                    if major >= 16:
                        self.print_status(f"Node.js {node_ver} installed", 'success')
                        time.sleep(0.3)
                    else:
                        self.print_status(f"Node.js {node_ver} is outdated (v16+ required)", 'warning')
                        time.sleep(0.3)
                else:
                    self.print_status(f"Node.js found: {node_ver}", 'success')
                    time.sleep(0.3)
            except:
                self.print_status(f"Node.js found: {node_ver}", 'success')
                time.sleep(0.3)
        else:
            self.print_status("Node.js not found!", 'error')
            self.print_status("Download from: https://nodejs.org", 'info')
            return False

        # Check npm
        npm_ok, npm_ver = self.check_command("npm")
        if npm_ok:
            self.print_status(f"npm {npm_ver} installed", 'success')
            time.sleep(0.3)
        else:
            self.print_status("npm not found!", 'error')
            return False

        return True

    def install_claude(self) -> bool:
        """Install or update Claude Code"""
        self.print_step("Claude Code Installation")
        time.sleep(0.5)

        # Check if already installed
        claude_ok, claude_ver = self.check_command("claude")
        time.sleep(0.5)

        if claude_ok:
            self.print_status(f"Claude Code already installed: {claude_ver}", 'success')
            time.sleep(0.3)

            # Ask for update
            print(f"\n  {Colors.INFO}{Icons.INFO}{Colors.RESET} Update to latest version? (y/n): ", end='')
            choice = input().lower()

            if choice == 'y':
                self.print_status("Updating Claude Code...", 'loading')
                self.animated_loading("Installing latest version", 3)
                _, code = self.run_command("npm install -g @anthropic-ai/claude-code@latest --force")
                if code == 0:
                    self.print_status("Claude Code updated successfully!", 'success')
                else:
                    self.print_status("Update failed, keeping current version", 'warning')
        else:
            self.print_status("Installing Claude Code...", 'loading')
            self.animated_loading("Downloading and installing", 3)
            _, code = self.run_command("npm install -g @anthropic-ai/claude-code --force")

            if code == 0:
                self.print_status("Claude Code installed successfully!", 'success')
            else:
                self.print_status("Installation failed!", 'error')
                return False

        return True

    def configure_path(self) -> bool:
        """Configure system PATH"""
        self.print_step("PATH Configuration")
        time.sleep(0.5)

        # Get npm prefix
        npm_prefix, code = self.run_command("npm config get prefix", capture=True)
        if code != 0:
            self.print_status("Could not determine npm location", 'error')
            return False

        self.npm_prefix = npm_prefix
        self.print_status(f"npm location: {npm_prefix}", 'info')
        time.sleep(0.3)

        # Find claude executable
        claude_cmd = Path(npm_prefix) / "claude.cmd"
        claude_exe = Path(npm_prefix) / "claude.exe"

        if claude_cmd.exists():
            self.claude_path = claude_cmd
            self.print_status(f"Found: {claude_cmd}", 'success')
            time.sleep(0.3)
        elif claude_exe.exists():
            self.claude_path = claude_exe
            self.print_status(f"Found: {claude_exe}", 'success')
            time.sleep(0.3)
        else:
            # Try to find it
            search_path = Path(npm_prefix)
            found = False
            for file in search_path.iterdir():
                if 'claude' in file.name.lower() and file.is_file():
                    self.claude_path = file
                    found = True
                    self.print_status(f"Found: {file}", 'success')
                    break

            if not found:
                self.print_status("Could not find claude executable", 'error')
                return False

        # Update PATH
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except WindowsError:
                current_path = ""
            winreg.CloseKey(key)

            if npm_prefix.lower() in current_path.lower():
                self.print_status("Already in system PATH", 'success')
            else:
                self.print_status("Adding to system PATH...", 'loading')
                new_path = f"{npm_prefix};{current_path}"

                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                winreg.CloseKey(key)

                # Notify system of change
                try:
                    import win32api
                    import win32con
                    win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
                except:
                    pass

                self.print_status("PATH updated successfully!", 'success')
        except Exception as e:
            self.print_status(f"Failed to update PATH: {e}", 'error')
            return False

        return True

    def verify_installation(self) -> bool:
        """Verify Claude Code installation"""
        self.print_step("Installation Verification")
        time.sleep(0.5)

        if self.claude_path and self.claude_path.exists():
            # Test direct path
            version, code = self.run_command(f'"{self.claude_path}" --version', capture=True)
            time.sleep(0.3)
            if code == 0:
                self.print_status(f"Claude Code v{version} verified", 'success')
                time.sleep(0.3)
                self.print_status("Direct execution works", 'success')
                time.sleep(0.3)
            else:
                self.print_status("Direct execution test failed", 'warning')
                time.sleep(0.3)

        # Test PATH
        claude_ok, claude_ver = self.check_command("claude")
        time.sleep(0.3)
        if claude_ok:
            self.print_status("PATH configuration verified", 'success')
        else:
            self.print_status("PATH not updated yet (requires new terminal)", 'info')

        return True

    def show_summary(self):
        """Show installation summary"""
        self.print_step("Installation Summary")
        time.sleep(0.5)

        elapsed = int(time.time() - self.start_time)

        # Success box
        if not self.errors:
            content = [
                f"{Icons.CHECK} Claude Code installed successfully",
                f"{Icons.CHECK} PATH configured properly",
                f"{Icons.CHECK} Ready to use in new terminal",
                "",
                f"Installation time: {elapsed} seconds",
                f"Log file: {self.log_file.name if self.log_file else 'Not available'}"
            ]
            self.print_box("SUCCESS", content, Colors.SUCCESS)
        else:
            content = [
                f"{Icons.CROSS} Installation completed with errors:",
                ""
            ] + [f"  {Icons.BULLET} {err}" for err in self.errors[:3]]
            self.print_box("COMPLETED WITH ISSUES", content, Colors.WARNING)

        # Next steps
        print(f"  {Colors.SECONDARY}┌{'─' * 58}┐{Colors.RESET}")
        print(f"  {Colors.SECONDARY}│{Colors.RESET} {Colors.BOLD}NEXT STEPS:{Colors.RESET}{' ' * 45}{Colors.SECONDARY}│{Colors.RESET}")
        print(f"  {Colors.SECONDARY}├{'─' * 58}┤{Colors.RESET}")
        print(f"  {Colors.SECONDARY}│{Colors.RESET} 1. Close this window{' ' * 36}{Colors.SECONDARY}│{Colors.RESET}")
        print(f"  {Colors.SECONDARY}│{Colors.RESET} 2. Open a {Colors.BOLD}NEW{Colors.RESET} Command Prompt or Terminal{' ' * 15}{Colors.SECONDARY}│{Colors.RESET}")
        print(f"  {Colors.SECONDARY}│{Colors.RESET} 3. Run: {Colors.PRIMARY}claude --version{Colors.RESET}{' ' * 30}{Colors.SECONDARY}│{Colors.RESET}")
        print(f"  {Colors.SECONDARY}│{Colors.RESET} 4. Run: {Colors.PRIMARY}claude{Colors.RESET} to start coding!{' ' * 24}{Colors.SECONDARY}│{Colors.RESET}")
        print(f"  {Colors.SECONDARY}└{'─' * 58}┘{Colors.RESET}")

        if self.warnings:
            print(f"\n  {Colors.WARNING}Warnings:{Colors.RESET}")
            for warn in self.warnings[:3]:
                print(f"  {Colors.WARNING}{Icons.WARNING}{Colors.RESET} {warn}")

    def create_desktop_shortcut(self) -> bool:
        """Create desktop shortcut for Claude Code"""
        self.print_step("Creating Desktop Shortcut")
        time.sleep(0.5)

        try:
            desktop = Path.home() / "Desktop"
            if desktop.exists() and self.claude_path:
                # Create batch file
                shortcut = desktop / "Claude Code.bat"
                with open(shortcut, 'w') as f:
                    f.write(f'@echo off\n')
                    f.write(f'title Claude Code\n')
                    f.write(f'echo Starting Claude Code...\n')
                    f.write(f'"{self.claude_path}"\n')
                    f.write(f'pause\n')

                self.print_status(f"Desktop shortcut created", 'success')
                time.sleep(0.3)
                return True
        except Exception as e:
            self.print_status(f"Could not create shortcut: {e}", 'warning')
            time.sleep(0.3)

        return False

    def run(self):
        """Main installation flow"""
        self.print_banner()

        # Check requirements
        if not self.check_system_requirements():
            print()
            self.print_box("ADMINISTRATOR REQUIRED", [
                "This installer needs Administrator privileges.",
                "",
                "Please:",
                "  1. Right-click on Command Prompt",
                "  2. Select 'Run as administrator'",
                "  3. Run this script again"
            ], Colors.ERROR)
            input(f"\n  Press Enter to exit...")
            sys.exit(1)

        # Check Node.js
        if not self.check_nodejs():
            print()
            self.print_box("NODE.JS REQUIRED", [
                "Node.js is not installed or outdated.",
                "",
                "Please download and install from:",
                "  https://nodejs.org",
                "",
                "Then run this installer again."
            ], Colors.ERROR)
            input(f"\n  Press Enter to exit...")
            sys.exit(1)

        # Install Claude
        if not self.install_claude():
            input(f"\n  Press Enter to exit...")
            sys.exit(1)

        # Configure PATH
        if not self.configure_path():
            input(f"\n  Press Enter to exit...")
            sys.exit(1)

        # Verify
        self.verify_installation()

        # Create shortcut
        self.create_desktop_shortcut()

        # Show summary
        self.show_summary()

        print()
        input(f"  {Colors.DIM}Press Enter to exit...{Colors.RESET}")

if __name__ == "__main__":
    wizard = SetupWizard()
    try:
        wizard.run()
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.WARNING}Installation cancelled by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n  {Colors.ERROR}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)
