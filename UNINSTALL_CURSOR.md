# Uninstalling Cursor

This guide provides instructions for completely uninstalling Cursor from your system.

## Table of Contents

- [Linux](#linux)
- [macOS](#macos)
- [Windows](#windows)

---

## Linux

### Method 1: Using Package Manager (if installed via package manager)

If you installed Cursor using a package manager:

```bash
# For Debian/Ubuntu (if installed via .deb)
sudo apt remove cursor

# For Fedora/RHEL (if installed via .rpm)
sudo dnf remove cursor
# or
sudo yum remove cursor

# For Arch Linux (if installed via AUR)
yay -R cursor
# or
paru -R cursor
```

### Method 2: Manual Uninstallation

1. **Remove the application directory:**

```bash
# Common installation locations
sudo rm -rf /opt/Cursor
sudo rm -rf /usr/share/cursor
sudo rm -rf ~/.local/share/cursor
```

2. **Remove desktop entries and shortcuts:**

```bash
rm -f ~/.local/share/applications/cursor.desktop
sudo rm -f /usr/share/applications/cursor.desktop
```

3. **Remove user configuration and data:**

```bash
# Configuration files
rm -rf ~/.config/Cursor

# Cache
rm -rf ~/.cache/Cursor

# Local data
rm -rf ~/.local/share/Cursor
```

4. **Remove any symlinks:**

```bash
sudo rm -f /usr/bin/cursor
sudo rm -f /usr/local/bin/cursor
```

### Verification

To verify Cursor has been completely removed:

```bash
which cursor
# Should return nothing

find ~ -name "*cursor*" -o -name "*Cursor*" 2>/dev/null
# Check if any files remain
```

---

## macOS

### Method 1: Manual Uninstallation

1. **Quit Cursor:**

   - Ensure Cursor is not running
   - Press `Cmd + Q` or right-click the Cursor icon in the Dock and select "Quit"

2. **Remove the application:**

```bash
rm -rf /Applications/Cursor.app
```

3. **Remove user data and configuration:**

```bash
# Application Support
rm -rf ~/Library/Application\ Support/Cursor

# Preferences
rm -rf ~/Library/Preferences/com.cursor.*

# Caches
rm -rf ~/Library/Caches/Cursor
rm -rf ~/Library/Caches/com.cursor.*

# Logs
rm -rf ~/Library/Logs/Cursor

# Saved Application State
rm -rf ~/Library/Saved\ Application\ State/com.cursor.*
```

4. **Remove additional files:**

```bash
# Remove from ~/Library
find ~/Library -iname "*cursor*" -exec rm -rf {} + 2>/dev/null
```

### Method 2: Using AppCleaner (Recommended)

1. Download [AppCleaner](https://freemacsoft.net/appcleaner/) (free)
2. Drag Cursor.app into AppCleaner
3. AppCleaner will find all associated files
4. Click "Remove" to uninstall completely

### Verification

```bash
# Check if app exists
ls /Applications/Cursor.app
# Should return: No such file or directory

# Search for remaining files
find ~ -iname "*cursor*" 2>/dev/null
```

---

## Windows

### Method 1: Using Windows Settings (Windows 10/11)

1. Open **Settings** (`Win + I`)
2. Go to **Apps** > **Apps & features**
3. Search for **Cursor**
4. Click on Cursor and select **Uninstall**
5. Follow the uninstallation wizard

### Method 2: Using Control Panel

1. Open **Control Panel**
2. Go to **Programs** > **Programs and Features**
3. Find **Cursor** in the list
4. Right-click and select **Uninstall**
5. Follow the uninstallation wizard

### Method 3: Manual Uninstallation

If the above methods don't work:

1. **Remove the application directory:**

```powershell
# Run PowerShell as Administrator
Remove-Item -Path "$env:LOCALAPPDATA\Programs\Cursor" -Recurse -Force
```

2. **Remove user data and configuration:**

```powershell
# User data
Remove-Item -Path "$env:APPDATA\Cursor" -Recurse -Force

# Local data
Remove-Item -Path "$env:LOCALAPPDATA\Cursor" -Recurse -Force
```

3. **Remove shortcuts:**

```powershell
# Desktop shortcut
Remove-Item -Path "$env:USERPROFILE\Desktop\Cursor.lnk" -Force

# Start Menu shortcut
Remove-Item -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Cursor.lnk" -Force
```

4. **Clean registry entries (Advanced):**

```powershell
# Run Registry Editor (regedit) as Administrator
# Delete these keys if they exist:
# HKEY_CURRENT_USER\Software\Cursor
# HKEY_LOCAL_MACHINE\SOFTWARE\Cursor
```

⚠️ **Warning:** Be careful when editing the registry. Only delete entries you're certain about.

### Method 4: Using Uninstaller Utility

Use a third-party uninstaller like:
- [Revo Uninstaller](https://www.revouninstaller.com/)
- [IObit Uninstaller](https://www.iobit.com/en/advanceduninstaller.php)
- [Geek Uninstaller](https://geekuninstaller.com/)

These tools can find and remove leftover files and registry entries.

### Verification

```powershell
# Check if application exists
Test-Path "$env:LOCALAPPDATA\Programs\Cursor"
# Should return: False

# Search for remaining files
Get-ChildItem -Path "$env:LOCALAPPDATA" -Filter "*cursor*" -Recurse
Get-ChildItem -Path "$env:APPDATA" -Filter "*cursor*" -Recurse
```

---

## Additional Cleanup

### Remove Extensions and Workspaces (All Platforms)

If you want to completely remove all traces including extensions and workspace settings:

**Linux/macOS:**
```bash
rm -rf ~/.cursor
```

**Windows:**
```powershell
Remove-Item -Path "$env:USERPROFILE\.cursor" -Recurse -Force
```

### Remove Global Configuration (All Platforms)

**Linux/macOS:**
```bash
rm -rf ~/.config/cursor
```

**Windows:**
```powershell
Remove-Item -Path "$env:APPDATA\cursor" -Recurse -Force
```

---

## Troubleshooting

### "Permission Denied" Errors

- **Linux/macOS:** Run commands with `sudo`
- **Windows:** Run PowerShell as Administrator

### Application Still Appears in Menu

- **macOS:** Restart Finder: `killall Finder`
- **Windows:** Restart Explorer: `taskkill /f /im explorer.exe && start explorer.exe`
- **Linux:** Log out and log back in, or restart

### Files Cannot Be Deleted (Application Running)

1. Close Cursor completely
2. Check Task Manager/Activity Monitor for any running Cursor processes
3. End all Cursor-related processes
4. Try uninstalling again

---

## Need Help?

If you encounter issues during uninstallation:

1. Check if Cursor is still running and close it
2. Restart your computer and try again
3. Search for remaining files manually
4. Contact Cursor support for assistance

---

## Reinstallation

If you plan to reinstall Cursor:

1. Complete the uninstallation process above
2. Restart your computer
3. Download the latest version from [cursor.sh](https://cursor.sh)
4. Install following the platform-specific instructions
