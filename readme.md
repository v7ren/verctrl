
# versctrl

Lightweight version control CLI tool with smart file detection and PyQt6 GUI

## Overview

versctrl is a simple yet powerful version control tool designed for quick file backups with intelligent file detection. It provides both command-line and GUI interfaces for managing file versions.

## Features

- **Smart File Detection**: Automatically detect files based on various strategies
- **PyQt6 GUI**: Modern graphical interface for file selection
- **Gitignore Support**: Respects .gitignore patterns
- **Multiple Naming Schemes**: Version numbers, timestamps, or simple naming
- **Automatic Cleanup**: Configurable history retention
- **Statistics Dashboard**: Track your backups and files
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Requirements

- Python 3.7+
- PyQt6 (optional, for GUI features)
- lucide-py (optional, for better icons)

### Method 1: Install from PyPI (Recommended)

```bash
# Install versctrl globally
pip install versctrl

# With GUI support
pip install versctrl[gui]

# With all optional features
pip install versctrl[all]
```

After installation, `versctrl` will be available globally in your terminal from any directory.


### Verify Installation

```bash
# Check if versctrl is accessible
versctrl --help

# Check version
versctrl --version
```

### Setting Up PATH (If Needed)

If `versctrl` is not recognized after installation, you may need to add Python's Scripts directory to your PATH:

#### Windows

```powershell
# Find Python Scripts directory
python -m site --user-site

# Add to PATH (PowerShell - Admin)
$pythonScripts = python -c "import site; print(site.USER_BASE + '\\Scripts')"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pythonScripts", "User")

# Restart your terminal
```

Or manually:
1. Open "Environment Variables" settings
2. Edit "Path" under User variables
3. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X\Scripts`
4. Click OK and restart terminal

#### macOS/Linux

```bash
# Find Python Scripts directory
python3 -m site --user-base

# Add to PATH (add to ~/.bashrc, ~/.zshrc, or ~/.bash_profile)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Reload shell configuration
source ~/.bashrc

# For zsh users
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Verify PATH Setup

```bash
# Check if versctrl is in PATH
which versctrl  # macOS/Linux
where versctrl  # Windows

# Should output something like:
# /home/username/.local/bin/versctrl
# or C:\Users\Username\AppData\Local\Programs\Python\Python3X\Scripts\versctrl.exe
```

### Optional Dependencies

```bash
# Install GUI support separately
pip install PyQt6

# Install enhanced icons
pip install lucide-py

# Install all optional dependencies
pip install PyQt6 lucide-py
```

### Upgrading

```bash
# Upgrade to latest version
pip install --upgrade versctrl

# Upgrade with all features
pip install --upgrade versctrl[all]
```

### Uninstallation

```bash
pip uninstall versctrl
```

## Quick Start

### 1. Initialize Configuration

```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize versctrl
versctrl --init
```

This creates a `versctrl.json` configuration file in your current directory.

### 2. Select Files

#### Using GUI (Recommended)

```bash
versctrl --select
```

This launches a modern file browser with:
- Tree view of your project
- Smart detection strategies
- Search and filter capabilities
- Visual file type indicators

#### Using Smart Add (CLI)

```bash
# Add source files (respects .gitignore)
versctrl --smart-add smart

# Add Python files only
versctrl --smart-add python

# Add recently modified files
versctrl --smart-add recent --days 7

# Add web-related files
versctrl --smart-add web

# Add all non-excluded files
versctrl --smart-add all
```

### 3. Create Backup

```bash
versctrl --new
```

This creates backups of all tracked files according to your configuration.

### 4. List Backups

```bash
versctrl --list
```

Shows all existing backups with size and modification date.

### 5. Restore Backup

```bash
versctrl --restore filename-v1.txt
```

Restores a specific backup to its original location.

## Global Usage

Once installed, you can use `versctrl` from anywhere:

```bash
# Backup your documents
cd ~/Documents/important-project
versctrl --init
versctrl --smart-add smart
versctrl --new

# Backup your code
cd ~/Code/my-app
versctrl --init
versctrl --select
versctrl --new

# Use different configs for different projects
cd ~/project1
versctrl --config project1.json --new

cd ~/project2
versctrl --config project2.json --new
```

## Configuration

The `versctrl.json` file contains:

```json
{
  "files": [
    "src/main.py",
    "config.yaml",
    "README.md"
  ],
  "backup_dir": ".versctrl_backups",
  "naming_scheme": "version",
  "keep_history": 5,
  "create_new_file": false
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `files` | List of files to track | `[]` |
| `backup_dir` | Directory for backups | `.versctrl_backups` |
| `naming_scheme` | `version`, `timestamp`, or `simple` | `version` |
| `keep_history` | Number of backups to keep | `5` |
| `create_new_file` | Create empty file after backup | `false` |

### Naming Schemes

- **version**: `file-v1.txt`, `file-v2.txt`, `file-v3.txt`
- **timestamp**: `file-20240101-143022.txt`
- **simple**: `file-old.txt` (overwrites previous backup)

## Smart Detection Strategies

### smart (Recommended)

Detects source code files while respecting .gitignore patterns. Excludes:
- Version control directories (.git, .svn)
- Dependencies (node_modules, venv)
- Build artifacts (dist, build)
- IDE files (.idea, .vscode)
- Binary files

### source

All source code files regardless of .gitignore:
- Programming languages (.py, .js, .java, .cpp, etc.)
- Web files (.html, .css, .scss)
- Configuration (.json, .yaml, .toml)
- Documentation (.md, .rst, .txt)

### recent

Files modified within specified days:

```bash
versctrl --smart-add recent --days 7
```

### python

Python files only (.py)

### web

Web-related files:
- HTML, CSS, SCSS, SASS, LESS
- JavaScript, TypeScript
- Vue, Svelte components

### all

All files except default exclusions

## Command Reference

### Initialize

```bash
versctrl --init
```

Creates default configuration file.

### File Selection

```bash
# GUI selector
versctrl --select

# Smart add with strategy
versctrl --smart-add STRATEGY [--days N]
```

### Backup Operations

```bash
# Create new backup
versctrl --new

# List all backups
versctrl --list

# Restore specific backup
versctrl --restore FILENAME
```

### Information

```bash
# Show statistics
versctrl --stats

# Show version
versctrl --version

# Show help
versctrl --help

# Use custom config file
versctrl --config path/to/config.json
```

## Statistics

The `--stats` command shows:

- Number of tracked files
- Existing vs missing files
- Total size of tracked files
- File type distribution
- Backup count and size
- Oldest and newest backups
- Configuration summary

Example output:

```
============================================================
Statistics
============================================================

Tracked Files: 15
  Existing: 14
  Missing: 1
  Total Size: 2.45 MB

  Top File Types:
    .py: 8
    .json: 3
    .md: 2
    .yaml: 1
    .txt: 1

Backup Directory: .versctrl_backups
  Total Backups: 42
  Total Size: 12.3 MB
  Oldest: 2024-01-15 10:30:00
  Newest: 2024-01-20 14:22:15

Configuration:
  Naming Scheme: version
  Keep History: 5
  Create New File: False

============================================================
```

## Default Exclusions

versctrl automatically excludes:

### Version Control
- .git, .svn, .hg, .bzr

### Dependencies
- node_modules, bower_components, vendor
- venv, .venv, env, .env

### Python
- __pycache__, *.pyc, *.pyo
- *.egg-info, dist, build

### IDE
- .idea, .vscode, .vs
- *.swp, *.swo, *~

### OS
- .DS_Store, Thumbs.db, desktop.ini

### Build Artifacts
- *.o, *.so, *.dll, *.exe

### Temporary
- tmp, temp, .tmp, .cache
- *.log, logs
- *.bak, *.backup, *.old

## Gitignore Support

versctrl respects .gitignore patterns in your project root:

```gitignore
# Example .gitignore
node_modules/
*.log
.env
dist/
```

Files matching these patterns will be excluded from smart detection.

## GUI Features

The PyQt6 GUI provides:

### File Tree
- Hierarchical view of your project
- File type icons
- Size and modification date
- Checkbox selection

### Smart Detection Panel
- Strategy selector
- Days parameter for recent files
- One-click application

### Search and Filter
- Real-time search
- Filter by name or extension

### Bulk Operations
- Select all / Deselect all
- Expand all / Collapse all

### Visual Indicators
- Color-coded file types
- Size formatting
- Previously tracked files highlighted

## Use Cases

### Project Development

Track source files while excluding dependencies:

```bash
cd /path/to/project
versctrl --init
versctrl --smart-add smart
versctrl --new
```

### Configuration Management

Track config files only:

```bash
cd /path/to/configs
versctrl --init
# Manually edit versctrl.json to add config files
versctrl --new
```

### Document Versioning

Track recently modified documents:

```bash
cd ~/Documents/thesis
versctrl --init
versctrl --smart-add recent --days 7
versctrl --new
```

### Web Development

Track web project files:

```bash
cd ~/Sites/my-website
versctrl --init
versctrl --smart-add web
versctrl --new
```

### Multiple Projects

Manage backups across different projects:

```bash
# Setup project 1
cd ~/project1
versctrl --init
versctrl --smart-add smart
versctrl --new

# Setup project 2
cd ~/project2
versctrl --init
versctrl --smart-add python
versctrl --new

# Later, create backups from anywhere
cd ~/project1 && versctrl --new
cd ~/project2 && versctrl --new
```

## Best Practices

1. **Use Smart Detection**: Start with `--smart-add smart` for most projects
2. **Review Selection**: Use `--select` GUI to review auto-detected files
3. **Regular Backups**: Run `versctrl --new` before major changes
4. **Check Statistics**: Use `--stats` to monitor backup growth
5. **Adjust History**: Set `keep_history` based on your needs
6. **Custom Config**: Use `--config` for different project profiles
7. **Per-Project Setup**: Initialize versctrl in each project directory
8. **Backup Before Updates**: Create backups before major refactoring

## Troubleshooting

### Command Not Found

If `versctrl` is not recognized:

```bash
# Check if pip installed it correctly
pip show versctrl

# Check Python Scripts directory
python -m site --user-base

# Try running with python -m
python -m versctrl --help
```

Then add the Scripts directory to your PATH (see installation section).

### PyQt6 Not Found

```bash
pip install PyQt6
```

### Permission Denied

Ensure you have write permissions for:
- Configuration file location
- Backup directory
- Tracked files

On Unix systems:
```bash
chmod +x ~/.local/bin/versctrl
```

### Missing Files Warning

Files listed in config but not found on disk will show warnings. Update config with:

```bash
versctrl --select
```

### Large Backup Size

Reduce `keep_history` or exclude large files:

```json
{
  "keep_history": 3
}
```

### Import Errors

If you get import errors:

```bash
# Reinstall with all dependencies
pip uninstall versctrl
pip install versctrl[all]
```

## Advanced Usage

### Multiple Configurations

```bash
# Development config
versctrl --config dev.json --new

# Production config
versctrl --config prod.json --new

# Testing config
versctrl --config test.json --new
```

### Automation with Scripts

#### Bash Script (Linux/macOS)

```bash
#!/bin/bash
# backup-all.sh

projects=(
  "$HOME/Code/project1"
  "$HOME/Code/project2"
  "$HOME/Documents/thesis"
)

for project in "${projects[@]}"; do
  echo "Backing up $project..."
  cd "$project" && versctrl --new
done
```

#### PowerShell Script (Windows)

```powershell
# backup-all.ps1

$projects = @(
  "$env:USERPROFILE\Code\project1",
  "$env:USERPROFILE\Code\project2",
  "$env:USERPROFILE\Documents\thesis"
)

foreach ($project in $projects) {
  Write-Host "Backing up $project..."
  Set-Location $project
  versctrl --new
}
```

### Scheduled Backups

#### Linux/macOS (cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 6 PM
0 18 * * * cd /path/to/project && /home/user/.local/bin/versctrl --new

# Add hourly backup during work hours
0 9-17 * * 1-5 cd /path/to/project && /home/user/.local/bin/versctrl --new
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
5. Program: `versctrl`
6. Arguments: `--new`
7. Start in: `C:\path\to\project`

## Comparison with Git

| Feature | versctrl | Git |
|---------|---------|-----|
| Setup | Single command | Multiple commands |
| Learning Curve | Minimal | Moderate to steep |
| File Selection | GUI + Smart detection | Manual staging |
| Backup Speed | Fast | Fast |
| History | Configurable limit | Unlimited |
| Collaboration | No | Yes |
| Branching | No | Yes |
| Merge Conflicts | No | Yes |
| Global Install | Yes | Yes |
| Best For | Quick backups, solo work | Team projects, complex history |


## License

MIT License - See LICENSE file for details
