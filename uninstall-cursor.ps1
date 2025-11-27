# Cursor Uninstall Script for Windows
# Usage: .\uninstall-cursor.ps1 [-Full]
# Options:
#   -Full    Performs a complete uninstall including all user data and configurations

param(
    [switch]$Full = $false
)

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "Cursor Uninstall Script for Windows" -ForegroundColor Green
Write-Host ""

if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator." -ForegroundColor Yellow
    Write-Host "Some files may require administrator privileges to remove." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit
    }
}

# Function to remove path if it exists
function Remove-IfExists {
    param(
        [string]$Path
    )
    
    if (Test-Path $Path) {
        Write-Host "Removing: $Path" -ForegroundColor Gray
        try {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
        } catch {
            Write-Host "Error removing $Path : $_" -ForegroundColor Red
        }
    }
}

# Check if Cursor is running
Write-Host "Checking if Cursor is running..." -ForegroundColor Cyan
$cursorProcesses = Get-Process | Where-Object { $_.Name -like "*cursor*" }

if ($cursorProcesses) {
    Write-Host "Cursor is currently running." -ForegroundColor Yellow
    $quit = Read-Host "Would you like to quit Cursor now? (y/N)"
    
    if ($quit -eq "y" -or $quit -eq "Y") {
        Write-Host "Stopping Cursor processes..." -ForegroundColor Gray
        $cursorProcesses | ForEach-Object {
            try {
                Stop-Process -Id $_.Id -Force
            } catch {
                Write-Host "Warning: Could not stop process $($_.Name)" -ForegroundColor Yellow
            }
        }
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Please quit Cursor before uninstalling." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "Starting uninstallation..." -ForegroundColor Green
Write-Host ""

# Try to uninstall using Windows uninstaller
Write-Host "Attempting to uninstall via Windows installer..." -ForegroundColor Cyan

$uninstallKeys = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$cursorUninstaller = $null
foreach ($key in $uninstallKeys) {
    $apps = Get-ItemProperty $key -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*Cursor*" }
    if ($apps) {
        $cursorUninstaller = $apps.UninstallString
        break
    }
}

if ($cursorUninstaller) {
    Write-Host "Found Cursor uninstaller: $cursorUninstaller" -ForegroundColor Gray
    try {
        # Parse and execute uninstaller
        if ($cursorUninstaller -match '^"(.+?)"(.*)$') {
            $uninstallerPath = $matches[1]
            $uninstallerArgs = $matches[2].Trim()
        } else {
            $uninstallerPath = $cursorUninstaller
            $uninstallerArgs = ""
        }
        
        Start-Process -FilePath $uninstallerPath -ArgumentList "$uninstallerArgs /S" -Wait -NoNewWindow
        Write-Host "Uninstaller completed." -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not run uninstaller: $_" -ForegroundColor Yellow
        Write-Host "Proceeding with manual removal..." -ForegroundColor Yellow
    }
} else {
    Write-Host "No Windows uninstaller found. Proceeding with manual removal..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Removing application directories..." -ForegroundColor Cyan

# Remove application directories
Remove-IfExists "$env:LOCALAPPDATA\Programs\Cursor"
Remove-IfExists "$env:LOCALAPPDATA\Programs\cursor"

# Remove user data and configuration
Write-Host "Removing user data and configuration..." -ForegroundColor Cyan
Remove-IfExists "$env:APPDATA\Cursor"
Remove-IfExists "$env:LOCALAPPDATA\Cursor"

# Remove shortcuts
Write-Host "Removing shortcuts..." -ForegroundColor Cyan
Remove-IfExists "$env:USERPROFILE\Desktop\Cursor.lnk"
Remove-IfExists "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Cursor.lnk"
Remove-IfExists "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Cursor"

# Full uninstall
if ($Full) {
    Write-Host ""
    Write-Host "Performing full uninstall (including all user data)..." -ForegroundColor Yellow
    
    Remove-IfExists "$env:USERPROFILE\.cursor"
    Remove-IfExists "$env:APPDATA\cursor"
    
    # Clean registry entries
    if ($isAdmin) {
        Write-Host "Cleaning registry entries..." -ForegroundColor Cyan
        
        $registryPaths = @(
            "HKCU:\Software\Cursor",
            "HKLM:\SOFTWARE\Cursor",
            "HKLM:\SOFTWARE\WOW6432Node\Cursor"
        )
        
        foreach ($regPath in $registryPaths) {
            if (Test-Path $regPath) {
                try {
                    Remove-Item -Path $regPath -Recurse -Force
                    Write-Host "Removed registry key: $regPath" -ForegroundColor Gray
                } catch {
                    Write-Host "Warning: Could not remove registry key $regPath : $_" -ForegroundColor Yellow
                }
            }
        }
    } else {
        Write-Host "Skipping registry cleanup (requires Administrator privileges)" -ForegroundColor Yellow
    }
    
    # Search for remaining files
    Write-Host "Searching for any remaining Cursor files..." -ForegroundColor Cyan
    $searchPaths = @(
        "$env:LOCALAPPDATA",
        "$env:APPDATA"
    )
    
    foreach ($searchPath in $searchPaths) {
        Get-ChildItem -Path $searchPath -Filter "*cursor*" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-IfExists $_.FullName
        }
    }
}

Write-Host ""
Write-Host "Uninstallation complete!" -ForegroundColor Green
Write-Host ""

# Verification
Write-Host "Verifying uninstallation..." -ForegroundColor Cyan
$foundFiles = $false

$checkPaths = @(
    "$env:LOCALAPPDATA\Programs\Cursor",
    "$env:APPDATA\Cursor",
    "$env:LOCALAPPDATA\Cursor"
)

foreach ($path in $checkPaths) {
    if (Test-Path $path) {
        Write-Host "Warning: $path still exists" -ForegroundColor Yellow
        $foundFiles = $true
    }
}

if (-not $foundFiles) {
    Write-Host "✓ Cursor has been successfully uninstalled!" -ForegroundColor Green
} else {
    Write-Host "⚠ Some Cursor files may still remain. Please check manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Thank you for using Cursor!" -ForegroundColor Cyan
Write-Host ""

if (-not $Full) {
    Write-Host "Tip: Run with -Full flag to remove all user data and configurations" -ForegroundColor Yellow
}

# Prompt to restart Explorer
Write-Host ""
$restart = Read-Host "Would you like to restart Windows Explorer to refresh the UI? (y/N)"
if ($restart -eq "y" -or $restart -eq "Y") {
    Write-Host "Restarting Explorer..." -ForegroundColor Gray
    Stop-Process -Name explorer -Force
    Start-Process explorer
}
