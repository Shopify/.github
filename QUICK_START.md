# Quick Start: Uninstall Cursor Now

Choose your operating system and follow the commands:

---

## 🐧 Linux / 🍎 macOS

### 1. Open Terminal

### 2. Make script executable:
```bash
chmod +x uninstall-cursor.sh
```

### 3. Run uninstall:

**Basic uninstall:**
```bash
./uninstall-cursor.sh
```

**Complete uninstall (removes all data):**
```bash
./uninstall-cursor.sh --full
```

### Done! ✅

---

## 🪟 Windows

### 1. Open PowerShell as Administrator
- Press `Win + X`
- Click "Terminal (Admin)" or "PowerShell (Admin)"

### 2. If blocked, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### 3. Run uninstall:

**Basic uninstall:**
```powershell
.\uninstall-cursor.ps1
```

**Complete uninstall (removes all data):**
```powershell
.\uninstall-cursor.ps1 -Full
```

### Done! ✅

---

## What's the Difference?

| Type | What Gets Removed |
|------|-------------------|
| **Basic** | App files, cache, shortcuts |
| **Full** | Everything above + settings, extensions, workspaces |

---

## Having Issues?

- **"Permission denied"** → Run as admin (Windows) or use `chmod +x` (Linux/macOS)
- **"Cursor is running"** → Close Cursor completely first
- **Script won't run** → See `HOW_TO_UNINSTALL.md` for troubleshooting

---

Need detailed instructions? → See `HOW_TO_UNINSTALL.md`
