# Cursor Uninstall Tools

This directory contains tools and documentation for uninstalling Cursor from your system.

## Files

- **UNINSTALL_CURSOR.md** - Comprehensive manual uninstall guide for all platforms
- **uninstall-cursor.sh** - Automated uninstall script for Linux and macOS
- **uninstall-cursor.ps1** - Automated uninstall script for Windows

## Quick Start

### Linux / macOS

#### Basic Uninstall
```bash
./uninstall-cursor.sh
```

#### Complete Uninstall (removes all user data)
```bash
./uninstall-cursor.sh --full
```

### Windows

#### Basic Uninstall
```powershell
.\uninstall-cursor.ps1
```

#### Complete Uninstall (removes all user data)
```powershell
.\uninstall-cursor.ps1 -Full
```

**Note:** For best results on Windows, run PowerShell as Administrator.

## What Gets Removed

### Basic Uninstall
- Cursor application files
- Application support files
- Caches
- Desktop shortcuts
- Start menu entries

### Full Uninstall (--full or -Full flag)
All of the above, plus:
- User preferences and settings
- Extensions
- Workspace configurations
- All hidden configuration directories
- Registry entries (Windows only, requires admin)

## Prerequisites

### Linux / macOS
- Bash shell
- sudo access (for system-wide installations)

### Windows
- PowerShell 5.1 or later
- Administrator privileges (recommended)

## Safety Features

Both scripts include:
- ✅ Detection of running Cursor instances
- ✅ Confirmation prompts before removal
- ✅ Verification after uninstallation
- ✅ Safe file removal (only removes if exists)
- ✅ Colored output for better readability

## Troubleshooting

### "Permission Denied" Errors
- **Linux/macOS:** Ensure the script is executable (`chmod +x uninstall-cursor.sh`) and use `sudo` if needed
- **Windows:** Run PowerShell as Administrator

### Script Won't Run on macOS
macOS may block the script for security reasons:
```bash
chmod +x uninstall-cursor.sh
xattr -d com.apple.quarantine uninstall-cursor.sh
./uninstall-cursor.sh
```

### PowerShell Execution Policy Error
If Windows blocks the script:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\uninstall-cursor.ps1
```

## Manual Uninstallation

If you prefer to uninstall manually or the scripts don't work, see **UNINSTALL_CURSOR.md** for detailed step-by-step instructions for your platform.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the manual uninstall guide (UNINSTALL_CURSOR.md)
3. Ensure Cursor is completely closed before uninstalling
4. Restart your computer and try again

## After Uninstallation

To verify Cursor is completely removed:

**Linux/macOS:**
```bash
which cursor
find ~ -name "*cursor*" -o -name "*Cursor*" 2>/dev/null
```

**Windows:**
```powershell
Get-Command cursor -ErrorAction SilentlyContinue
Get-ChildItem -Path $env:LOCALAPPDATA -Filter "*cursor*"
Get-ChildItem -Path $env:APPDATA -Filter "*cursor*"
```

## Reinstallation

If you decide to reinstall Cursor:
1. Restart your computer after uninstallation
2. Download the latest version from [cursor.sh](https://cursor.sh)
3. Follow the installation instructions for your platform

---

**Note:** These scripts are provided as-is. Always backup important data before uninstalling any software.
