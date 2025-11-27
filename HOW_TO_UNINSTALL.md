# How to Complete Cursor Uninstallation

This guide shows you exactly how to uninstall Cursor using the provided tools.

## Step-by-Step Instructions

### For Linux or macOS Users

#### Step 1: Download the Script
If you don't have the script yet, download or copy `uninstall-cursor.sh` to your computer.

#### Step 2: Open Terminal
Open your terminal application.

#### Step 3: Navigate to Script Location
```bash
cd /path/to/script/directory
```

#### Step 4: Make Script Executable (if not already)
```bash
chmod +x uninstall-cursor.sh
```

#### Step 5: Choose Your Uninstall Type

**Option A: Basic Uninstall (removes application only)**
```bash
./uninstall-cursor.sh
```

**Option B: Complete Uninstall (removes everything including user data)**
```bash
./uninstall-cursor.sh --full
```

#### Step 6: Follow the Prompts
- The script will check if Cursor is running
- If running, it will ask if you want to quit it
- Answer `y` for yes or `n` for no
- The script will remove all Cursor files
- It will verify the uninstallation when complete

---

### For Windows Users

#### Step 1: Download the Script
Download or copy `uninstall-cursor.ps1` to your computer.

#### Step 2: Open PowerShell as Administrator
- Press `Win + X`
- Select "Windows PowerShell (Admin)" or "Terminal (Admin)"
- Or search for "PowerShell", right-click, and select "Run as administrator"

#### Step 3: Navigate to Script Location
```powershell
cd C:\path\to\script\directory
```

#### Step 4: Allow Script Execution (if needed)
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

#### Step 5: Choose Your Uninstall Type

**Option A: Basic Uninstall (removes application only)**
```powershell
.\uninstall-cursor.ps1
```

**Option B: Complete Uninstall (removes everything including user data)**
```powershell
.\uninstall-cursor.ps1 -Full
```

#### Step 6: Follow the Prompts
- The script will check if Cursor is running
- If running, it will ask if you want to quit it
- Answer `y` for yes or `n` for no
- The script will remove all Cursor files
- At the end, it may ask if you want to restart Windows Explorer
- It will verify the uninstallation when complete

---

## What Happens During Uninstallation

### Basic Uninstall Removes:
- ✅ Cursor application files
- ✅ Application cache
- ✅ Desktop shortcuts
- ✅ Start menu entries (Windows)
- ✅ System integrations

### Full Uninstall Removes:
- ✅ Everything from basic uninstall
- ✅ All user settings and preferences
- ✅ Extensions and workspaces
- ✅ Hidden configuration directories
- ✅ Registry entries (Windows, requires admin)

---

## Verification

After uninstallation, verify Cursor is removed:

### Linux/macOS:
```bash
# Check if command exists
which cursor

# Search for remaining files (should return nothing or very little)
find ~ -name "*cursor*" -o -name "*Cursor*" 2>/dev/null
```

### Windows:
```powershell
# Check if command exists
Get-Command cursor -ErrorAction SilentlyContinue

# Search for remaining files
Get-ChildItem -Path $env:LOCALAPPDATA -Filter "*cursor*"
Get-ChildItem -Path $env:APPDATA -Filter "*cursor*"
```

---

## Troubleshooting

### "Permission Denied" Error

**Linux/macOS:**
```bash
# Make script executable
chmod +x uninstall-cursor.sh

# Or run with sudo (not recommended for user files)
sudo ./uninstall-cursor.sh
```

**Windows:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell -> Run as Administrator
```

### "Cursor is Running" Warning

1. Close all Cursor windows
2. Check system tray/taskbar for running instance
3. Open Task Manager (Windows) or Activity Monitor (macOS):
   - End all Cursor processes
4. Run the uninstall script again

### Script Won't Run on macOS (Security Block)

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine uninstall-cursor.sh

# Then run the script
./uninstall-cursor.sh
```

### PowerShell Script Blocked on Windows

```powershell
# Temporarily bypass execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Then run the script
.\uninstall-cursor.ps1
```

### Manual Uninstall Needed

If the scripts don't work, see `UNINSTALL_CURSOR.md` for complete manual uninstall instructions.

---

## After Uninstallation

### Clean Up Installation
It's recommended to restart your computer after uninstalling to ensure all processes are terminated and files are released.

### Reinstall (If Needed)
If you want to reinstall Cursor:
1. Restart your computer
2. Visit [cursor.sh](https://cursor.sh)
3. Download and install the latest version

---

## Quick Reference

| Platform | Basic Command | Full Uninstall Command |
|----------|--------------|----------------------|
| Linux/macOS | `./uninstall-cursor.sh` | `./uninstall-cursor.sh --full` |
| Windows | `.\uninstall-cursor.ps1` | `.\uninstall-cursor.ps1 -Full` |

---

## Need More Help?

1. **For detailed manual steps**: See `UNINSTALL_CURSOR.md`
2. **For script details**: See `UNINSTALL_README.md`
3. **Still having issues**: Restart your computer and try again

---

**Important Notes:**
- ⚠️ The full uninstall will delete ALL your Cursor settings, extensions, and workspaces
- ⚠️ Make sure to backup any important settings before full uninstall
- ⚠️ Close Cursor completely before running the uninstall script
