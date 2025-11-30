# How to Uninstall Claude

This guide provides instructions for completely uninstalling the Claude desktop application from your system.

## macOS

### Method 1: Using Finder

1. **Quit Claude**
   - Right-click the Claude icon in the Dock
   - Select "Quit" or press `Cmd + Q` when the app is active

2. **Remove the Application**
   - Open Finder
   - Go to the Applications folder (`Cmd + Shift + A`)
   - Find the Claude app
   - Drag Claude to the Trash, or right-click and select "Move to Trash"

3. **Remove Application Support Files** (Optional)
   - Open Finder and press `Cmd + Shift + G` to open "Go to Folder"
   - Navigate to `~/Library/Application Support/` and delete the `Claude` folder if it exists
   - Navigate to `~/Library/Caches/` and delete any `Claude` or `com.anthropic.claude` folders
   - Navigate to `~/Library/Preferences/` and delete any files starting with `com.anthropic.claude`

4. **Empty Trash**
   - Right-click the Trash icon in the Dock
   - Select "Empty Trash"

### Method 2: Using Terminal

```bash
# Quit Claude if running
osascript -e 'quit app "Claude"'

# Remove the application
sudo rm -rf /Applications/Claude.app

# Remove application support files
rm -rf ~/Library/Application\ Support/Claude
rm -rf ~/Library/Caches/Claude
rm -rf ~/Library/Caches/com.anthropic.claude*
rm -rf ~/Library/Preferences/com.anthropic.claude*
rm -rf ~/Library/Saved\ Application\ State/com.anthropic.claude*
```

## Windows

### Method 1: Using Settings

1. **Close Claude**
   - Right-click the Claude icon in the system tray
   - Select "Quit" or close all Claude windows

2. **Uninstall via Settings**
   - Open **Settings** (`Windows + I`)
   - Go to **Apps** > **Apps & features** or **Installed apps**
   - Search for "Claude"
   - Click on Claude and select **Uninstall**
   - Follow the uninstallation prompts

### Method 2: Using Control Panel

1. **Close Claude** (as above)

2. **Uninstall via Control Panel**
   - Open **Control Panel**
   - Go to **Programs** > **Programs and Features**
   - Find "Claude" in the list
   - Right-click and select **Uninstall**
   - Follow the uninstallation wizard

### Method 3: Remove Residual Files (Optional)

After uninstalling, you may want to remove leftover files:

1. Press `Windows + R` to open Run dialog
2. Type `%APPDATA%` and press Enter
3. Delete the `Claude` folder if it exists
4. Type `%LOCALAPPDATA%` in Run dialog
5. Delete the `Claude` folder if it exists

## Linux

### Ubuntu/Debian-based Systems

#### If installed via .deb package:

```bash
# Remove the package
sudo apt remove claude
# or
sudo dpkg -r claude

# Remove configuration files
sudo apt purge claude
# or
sudo dpkg --purge claude

# Clean up residual files
rm -rf ~/.config/Claude
rm -rf ~/.local/share/Claude
rm -rf ~/.cache/Claude
```

#### If installed via Snap:

```bash
# Remove the snap package
sudo snap remove claude
```

### Fedora/RHEL-based Systems

```bash
# If installed via RPM
sudo dnf remove claude
# or
sudo rpm -e claude

# Clean up residual files
rm -rf ~/.config/Claude
rm -rf ~/.local/share/Claude
rm -rf ~/.cache/Claude
```

### Arch Linux

```bash
# If installed via pacman
sudo pacman -R claude

# Remove configuration files
rm -rf ~/.config/Claude
rm -rf ~/.local/share/Claude
rm -rf ~/.cache/Claude
```

### AppImage Installation

If you installed Claude as an AppImage:

```bash
# Remove the AppImage file
rm ~/Downloads/Claude*.AppImage  # or wherever you stored it

# Remove configuration files
rm -rf ~/.config/Claude
rm -rf ~/.local/share/Claude
rm -rf ~/.cache/Claude
```

## Verification

After uninstalling, you can verify that Claude has been removed:

### macOS
```bash
# Check if app exists
ls -la /Applications/Claude.app
# Should return: "No such file or directory"
```

### Windows
```powershell
# Check installed programs
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where-Object { $_.DisplayName -like "*Claude*" }
# Should return nothing if fully uninstalled
```

### Linux
```bash
# Check if executable exists
which claude
# Should return nothing if fully uninstalled
```

## Reinstalling Claude

If you want to reinstall Claude in the future, you can download it from the official Anthropic website or your organization's software portal.

## Need Help?

If you encounter any issues during the uninstallation process, please contact your IT support team or refer to your organization's support resources.
