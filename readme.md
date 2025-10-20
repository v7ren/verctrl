# verctrl

Lightweight version control CLI tool with smart file detection and PyQt6 GUI

## Overview

verctrl is a simple yet powerful version control tool designed for quick file backups with intelligent file detection. It provides both command-line and GUI interfaces for managing file versions.

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

### Install Dependencies

```bash
# Core functionality only
pip install verctrl

# With GUI support
pip install PyQt6

# With enhanced icons
pip install lucide-py
```

## Quick Start

### 1. Initialize Configuration

```bash
verctrl --init
```

This creates a `verctrl.json` configuration file in your current directory.

### 2. Select Files

#### Using GUI (Recommended)

```bash
verctrl --select
```

This launches a modern file browser with:
- Tree view of your project
- Smart detection strategies
- Search and filter capabilities
- Visual file type indicators

#### Using Smart Add (CLI)

```bash
# Add source files (respects .gitignore)
verctrl --smart-add smart

# Add Python files only
verctrl --smart-add python

# Add recently modified files
verctrl --smart-add recent --days 7

# Add web-related files
verctrl --smart-add web

# Add all non-excluded files
verctrl --smart-add all
```

### 3. Create Backup

```bash
verctrl --new
```

This creates backups of all tracked files according to your configuration.

### 4. List Backups

```bash
verctrl --list
```

Shows all existing backups with size and modification date.

### 5. Restore Backup

```bash
verctrl --restore filename-v1.txt
```

Restores a specific backup to its original location.

## Configuration

The `verctrl.json` file contains:

```json
{
  "files": [
    "src/main.py",
    "config.yaml",
    "README.md"
  ],
  "backup_dir": ".verctrl_backups",
  "naming_scheme": "version",
  "keep_history": 5,
  "create_new_file": false
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `files` | List of files to track | `[]` |
| `backup_dir` | Directory for backups | `.verctrl_backups` |
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
verctrl --smart-add recent --days 7
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
verctrl --init
```

Creates default configuration file.

### File Selection

```bash
# GUI selector
verctrl --select

# Smart add with strategy
verctrl --smart-add STRATEGY [--days N]
```

### Backup Operations

```bash
# Create new backup
verctrl --new

# List all backups
verctrl --list

# Restore specific backup
verctrl --restore FILENAME
```

### Information

```bash
# Show statistics
verctrl --stats

# Use custom config file
verctrl --config path/to/config.json
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

Backup Directory: .verctrl_backups
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

verctrl automatically excludes:

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

verctrl respects .gitignore patterns in your project root:

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
verctrl --init
verctrl --smart-add smart
verctrl --new
```

### Configuration Management

Track config files only:

```bash
verctrl --init
# Manually edit verctrl.json to add config files
verctrl --new
```

### Document Versioning

Track recently modified documents:

```bash
verctrl --init
verctrl --smart-add recent --days 7
verctrl --new
```

### Web Development

Track web project files:

```bash
verctrl --init
verctrl --smart-add web
verctrl --new
```

## Best Practices

1. **Use Smart Detection**: Start with `--smart-add smart` for most projects
2. **Review Selection**: Use `--select` GUI to review auto-detected files
3. **Regular Backups**: Run `verctrl --new` before major changes
4. **Check Statistics**: Use `--stats` to monitor backup growth
5. **Adjust History**: Set `keep_history` based on your needs
6. **Custom Config**: Use `--config` for different project profiles

## Troubleshooting

### PyQt6 Not Found

```bash
pip install PyQt6
```

### Permission Denied

Ensure you have write permissions for:
- Configuration file location
- Backup directory
- Tracked files

### Missing Files Warning

Files listed in config but not found on disk will show warnings. Update config with:

```bash
verctrl --select
```

### Large Backup Size

Reduce `keep_history` or exclude large files:

```json
{
  "keep_history": 3
}
```

## Advanced Usage

### Multiple Configurations

```bash
# Development config
verctrl --config dev.json --new

# Production config
verctrl --config prod.json --new
```

## Comparison with Git

| Feature | verctrl | Git |
|---------|---------|-----|
| Setup | Single command | Multiple commands |
| Learning Curve | Minimal | Moderate to steep |
| File Selection | GUI + Smart detection | Manual staging |
| Backup Speed | Fast | Fast |
| History | Configurable limit | Unlimited |
| Collaboration | No | Yes |
| Branching | No | Yes |
| Best For | Quick backups, solo work | Team projects, complex history |

## License

MIT License - See LICENSE file for details