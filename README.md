# macOS Cache Cleaner 🧹

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful, safe, and user-friendly utility to identify and clean large cache directories from your Mac. Features both interactive arrow-key navigation and classic selection modes.

## ✨ Features

✅ **Interactive UI**: Navigate with arrow keys, delete with DELETE key  
✅ **Classic Mode**: Traditional numbered selection interface  
✅ **Safe Operation**: Automatically protects system-critical directories  
✅ **Smart Detection**: Finds caches ≥ 100MB across system and projects  
✅ **Project Cleanup**: Safely removes old build artifacts (node_modules, Rust targets - 1+ day old)  
✅ **Real-time Updates**: See space freed immediately in interactive mode  
✅ **Full Path Display**: Verify exactly what will be deleted  
✅ **No External Dependencies**: Uses only Python standard library  

## What It Cleans

**System & App Caches:**
- Application caches (`~/Library/Caches/*`)
- Browser caches (Safari, Chrome, Firefox, Opera)
- Application support caches
- System logs (`~/Library/Logs/*`)
- Container and sandbox caches
- WebKit local storage caches

**3rd Party Applications:**
- Unity Hub & Editor caches
- Chrome/Chromium (GPU, Shader, Application caches)
- VS Code (workspace storage, extensions, logs)
- Slack, Discord, Spotify caches
- Adobe application caches (media cache files)
- JetBrains IDEs (system caches, temp files)
- Docker, Figma caches

**Development Tools:**
- npm global cache (`~/.npm`) and `_cacache`
- Homebrew cache (Intel & Apple Silicon)
- Yarn, pip, Composer caches
- CocoaPods, Gradle, Maven caches
- Rust Cargo, Go module caches

**Project Dependencies:**
- `node_modules` directories in Node.js projects
- `target` directories in Rust projects (compilation artifacts)
- **Safety**: Only targets build directories that haven't been modified in 1+ days
- **Smart Detection**: Verifies projects by checking for `package.json` / `Cargo.toml`
- Scans common development folders: `~/Development`, `~/Projects`, `~/Code`, `~/Desktop`, etc.

## What It Protects

The cleaner automatically avoids these system-critical areas:
- Keychains and Preferences
- System frameworks and services
- Apple system components
- Login and security services
- Audio, fonts, and system resources

## Requirements

- macOS (tested on macOS 10.14+)
- Python 3.6 or later
- No external dependencies required

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Mac_Cleaner.git
cd Mac_Cleaner

# Make the script executable
chmod +x mac_cache_cleaner.py

# Run the cleaner
python3 mac_cache_cleaner.py
```

### Alternative: Direct Download

1. Download `mac_cache_cleaner.py` from this repository
2. Make it executable: `chmod +x mac_cache_cleaner.py`
3. Run: `python3 mac_cache_cleaner.py`

## 🖥️ Usage

### Interface Modes

The cleaner offers two interface modes:

#### 1. 🖱️ Interactive Mode (Recommended)
Navigate with arrow keys and delete items instantly:

```bash
python3 mac_cache_cleaner.py
# Choose option 1 for Interactive Mode
```

**Controls:**
- `↑/↓` Arrow keys to navigate
- `DELETE` or `D` key to remove selected item
- `ENTER` to view detailed information
- `ESC` or `Q` to quit

#### 2. 📝 Classic Mode
Traditional numbered selection:

```bash
python3 mac_cache_cleaner.py
# Choose option 2 for Classic Mode
```

**Process:**
1. **Scanning**: Scans for cache directories ≥ 100MB
2. **Selection**: Choose directories using numbers (e.g., `1 3 5` or `all`)
3. **Confirmation**: Type `DELETE` to confirm batch deletion

### Example Session

```
🧹 macOS Cache Cleaner
==================================================
🔍 Scanning ~/Library/ for cache directories...
   Looking for directories >= 100MB

📊 Found 3 cache directories >= 100MB:
================================================================================
 1. Library/Caches/com.google.Chrome
    Size: 245.3MB

 2. Library/Application Support/Firefox/Profiles/abc123/cache2
    Size: 156.7MB

 3. Library/Logs/DiagnosticReports
    Size: 123.4MB

💾 Total cache size: 525.4MB
================================================================================

🗑️  Select directories to delete:
   Enter numbers separated by spaces (e.g., '1 3 5')
   Enter 'all' to select all directories
   Enter 'quit' or 'q' to exit without deleting

Your selection: 1 2

⚠️  FINAL CONFIRMATION
   You are about to permanently delete 2 directories
   Total size: 402.0MB

📁 Directories to delete:
   • Library/Caches/com.google.Chrome (245.3MB)
   • Library/Application Support/Firefox/Profiles/abc123/cache2 (156.7MB)

🚨 THIS ACTION CANNOT BE UNDONE!

Type 'DELETE' (in capitals) to proceed, or anything else to cancel: DELETE

🗑️  Deleting 2 directories...
   Deleting Library/Caches/com.google.Chrome... ✅ Done
   Deleting Library/Application Support/Firefox/Profiles/abc123/cache2... ✅ Done

📊 Deletion Summary:
   ✅ Successfully deleted: 2 directories (402.0MB)

✨ Cache cleaning completed!
```

## Safety Features

- **Whitelist-based scanning**: Only scans known safe cache locations
- **System protection**: Hardcoded blacklist of critical system directories
- **Manual confirmation**: Requires explicit user action for each deletion
- **No system files**: Cannot access or modify system-level directories
- **Time-based protection**: Build directories (`node_modules`, `target`) must be 1+ days old to be considered for deletion
- **Conservative approach**: When in doubt, the cleaner won't delete
- **Error handling**: Gracefully handles permission errors and missing files

## Troubleshooting

### Permission Denied Errors
Some directories may require elevated permissions. The cleaner will skip these and continue safely.

### No Cache Found
If no large cache directories are found, your system is already clean!

### Interrupted Process
Press `Ctrl+C` at any time to safely exit without making changes.

## Contributing

Feel free to submit issues or pull requests to improve the cleaner's functionality or safety features.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is designed to be safe, but always ensure you have important data backed up before running any cleanup utility. The authors are not responsible for any data loss.
