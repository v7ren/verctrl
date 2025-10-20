"""
verctrl - Lightweight version control CLI tool with smart file detection and PyQt6 GUI
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re
from typing import List, Set
import fnmatch
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import QByteArray, Qt
try:
    from lucide_py import get_icon_svg
    HAS_LUCIDE = True
except ImportError:
    HAS_LUCIDE = False
    print("⚠ lucide-py not installed. Using fallback icons.")
    print("  Install with: pip install lucide-py")
    
    FALLBACK_ICONS = {
        "folder": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>''',
        "file": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>''',
        "check": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>''',
        "x": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" x2="6" y2="18"/><line x1="6" x2="18" y2="18"/></svg>''',
        "save": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>''',
    }



from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QByteArray

def get_lucide_icon(icon_name: str, size: int = 16, color: str = "#000000") -> QIcon:
    """
    Get Lucide icon as QIcon
    Uses lucide-py if available, falls back to embedded icons
    """
    svg_string = None
    
    if HAS_LUCIDE:
        try:
            svg_string = get_icon_svg(icon_name)
        except Exception as e:
            print(f"⚠ lucide-py error for '{icon_name}': {e}")
    
    if svg_string is None:
        if icon_name in FALLBACK_ICONS:
            svg_string = FALLBACK_ICONS[icon_name]
        else:
            return QIcon()  
    
    try:
        svg_string = svg_string.replace('currentColor', color)
        
        svg_bytes = QByteArray(svg_string.encode())
        renderer = QSvgRenderer(svg_bytes)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    except Exception as e:
        print(f"⚠ Failed to render icon '{icon_name}': {e}")
        return QIcon()

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
        QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit,
        QLabel, QMessageBox, QCheckBox, QComboBox, QSpinBox,
        QGroupBox, QSplitter, QTextEdit
    )
    from PyQt6.QtCore import Qt, QSize, pyqtSignal
    from PyQt6.QtGui import QIcon, QFont, QColor, QPalette
    HAS_PYQT6 = True
except ImportError:
    HAS_PYQT6 = False
    print("⚠ PyQt6 not installed. Install with: pip install PyQt6")

def get_file_icon(file_path: Path) -> QIcon:
    """Get appropriate icon based on file type"""
    ext = file_path.suffix.lower()
    
    icon_map = {
        '.py': ("file-code", "#3776AB"),
        '.js': ("file-code", "#F7DF1E"),
        '.jsx': ("file-code", "#61DAFB"),
        '.ts': ("file-code", "#3178C6"),
        '.tsx': ("file-code", "#3178C6"),
        '.html': ("file-code", "#E34C26"),
        '.css': ("file-code", "#1572B6"),
        '.json': ("file-json", "#00ADD8"),
        '.yaml': ("file-json", "#CB171E"),
        '.yml': ("file-json", "#CB171E"),
        '.md': ("file-text", "#000000"),
        '.txt': ("file-text", "#666666"),
        '.png': ("image", "#9C27B0"),
        '.jpg': ("image", "#9C27B0"),
        '.jpeg': ("image", "#9C27B0"),
        '.gif': ("image", "#9C27B0"),
        '.svg': ("image", "#FF9800"),
    }
    
    icon_name, color = icon_map.get(ext, ("file", "#42A5F5"))
    return get_lucide_icon(icon_name, 16, color)


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GRAY = '\033[90m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}", file=sys.stderr)

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")




class GitignoreParser:
    """Parse and match .gitignore patterns"""
    
    def __init__(self, gitignore_path: Path = None):
        self.patterns = []
        self.load_gitignore(gitignore_path)
    
    def load_gitignore(self, gitignore_path: Path = None):
        """Load patterns from .gitignore file"""
        if gitignore_path is None:
            gitignore_path = Path.cwd() / '.gitignore'
        
        if not gitignore_path.exists():
            return
        
        try:
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.patterns.append(line)
        except Exception as e:
            print_warning(f"Failed to read .gitignore: {e}")
    
    def is_ignored(self, path: Path, root: Path) -> bool:
        """Check if path matches any gitignore pattern"""
        try:
            rel_path = str(path.relative_to(root))
        except ValueError:
            return False
        
        for pattern in self.patterns:
            if pattern.startswith('!'):
                continue
            
            if pattern.endswith('/'):
                if path.is_dir() and fnmatch.fnmatch(rel_path + '/', pattern):
                    return True
            else:
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
                    return True
                
                parts = Path(rel_path).parts
                for i in range(len(parts)):
                    if fnmatch.fnmatch(parts[i], pattern):
                        return True
        
        return False

class SmartFileDetector:
    """Smart file detection with various strategies"""
    
    DEFAULT_EXCLUDES = {
        '.git', '.svn', '.hg', '.bzr',
        'node_modules', 'bower_components', 'vendor',
        '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.Python',
        'venv', '.venv', 'env', '.env', 'ENV',
        '*.egg-info', 'dist', 'build', '.pytest_cache',
        '.idea', '.vscode', '.vs', '*.swp', '*.swo', '*~',
        '.DS_Store', 'Thumbs.db', 'desktop.ini',
        '*.o', '*.so', '*.dylib', '*.dll', '*.exe',
        '*.log', 'logs',
        '.verctrl_backups', '*.bak', '*.backup', '*.old',
        'tmp', 'temp', '.tmp', '.cache',
    }
    
    SOURCE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
        '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
        '.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.config',
        '.md', '.rst', '.txt', '.adoc',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.sql', '.graphql', '.proto',
    }
    
    BINARY_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
        '.mp4', '.avi', '.mov', '.wmv', '.flv',
        '.mp3', '.wav', '.ogg', '.flac',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    }
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.gitignore = GitignoreParser()
    
    def should_exclude_dir(self, dir_path: Path) -> bool:
        """Check if directory should be excluded"""
        dir_name = dir_path.name
        
        for pattern in self.DEFAULT_EXCLUDES:
            if not pattern.startswith('*'):
                if dir_name == pattern or dir_name.startswith('.'):
                    return True
        
        if self.gitignore.is_ignored(dir_path, self.root_path):
            return True
        
        return False
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded"""
        file_name = file_path.name
        
        for pattern in self.DEFAULT_EXCLUDES:
            if pattern.startswith('*'):
                if fnmatch.fnmatch(file_name, pattern):
                    return True
        
        if self.gitignore.is_ignored(file_path, self.root_path):
            return True
        
        if file_path.suffix.lower() in self.BINARY_EXTENSIONS:
            return True
        
        return False
    
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded (works for both files and directories)"""
        if path.is_dir():
            return self.should_exclude_dir(path)
        else:
            return self.should_exclude_file(path)
    
    def is_source_file(self, file_path: Path) -> bool:
        """Check if file is a source code file"""
        return file_path.suffix.lower() in self.SOURCE_EXTENSIONS
    
    def get_file_age_days(self, file_path: Path) -> float:
        """Get file age in days"""
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return (datetime.now() - mtime).total_seconds() / 86400
        except:
            return float('inf')
    
    def detect_files(self, strategy: str = 'smart', max_age_days: int = 30) -> List[Path]:
        """
        Detect files based on strategy:
        - 'smart': Source files, respecting gitignore
        - 'source': All source code files
        - 'recent': Files modified in last N days
        - 'python': Only Python files
        - 'web': Only web-related files
        - 'all': All non-excluded files
        """
        detected = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_dir():
                continue
            
            if self.should_exclude_file(file_path):
                continue
            
            skip = False
            for parent in file_path.parents:
                if parent == self.root_path:
                    break
                if self.should_exclude_dir(parent):
                    skip = True
                    break
            if skip:
                continue
            
            if strategy == 'smart':
                if self.is_source_file(file_path):
                    detected.append(file_path)
            
            elif strategy == 'source':
                if self.is_source_file(file_path):
                    detected.append(file_path)
            
            elif strategy == 'recent':
                if self.get_file_age_days(file_path) <= max_age_days:
                    detected.append(file_path)
            
            elif strategy == 'python':
                if file_path.suffix == '.py':
                    detected.append(file_path)
            
            elif strategy == 'web':
                web_exts = {'.html', '.css', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte'}
                if file_path.suffix.lower() in web_exts:
                    detected.append(file_path)
            
            elif strategy == 'all':
                detected.append(file_path)
        
        return sorted(detected)

class ModernFileTreeWidget(QTreeWidget):
    """Modern PyQt6 tree widget with checkboxes and smart features"""
    
    selectionChanged = pyqtSignal(int)  
    
    def __init__(self, root_path: Path, existing_files: Set[str] = None):
        super().__init__()
        self.root_path = root_path
        self.existing_files = existing_files or set()
        self.detector = SmartFileDetector(root_path)
        self.file_items = {}  
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tree widget UI with modern styling"""
        self.setHeaderLabels(['Name', 'Size', 'Type', 'Modified'])
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 150)
        
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(True)
        
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                font-size: 11pt;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
            }
            QTreeWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-right: 1px solid #dcdcdc;
                font-weight: bold;
            }
        """)
        
        self.itemChanged.connect(self.on_item_changed)
    
    def populate_tree(self, files: List[Path] = None):
        """Populate tree with files"""
        self.clear()
        self.file_items.clear()
        
        if files is None:
            files = []
            for file_path in self.root_path.rglob('*'):
                if file_path.is_file() and not self.detector.should_exclude_file(file_path):
                    skip = False
                    for parent in file_path.parents:
                        if parent == self.root_path:
                            break
                        if self.detector.should_exclude_dir(parent):
                            skip = True
                            break
                    if not skip:
                        files.append(file_path)
        
        dir_items = {}
        root_item = QTreeWidgetItem(self, [f"📁 {self.root_path.name}/", "", "Folder", ""])
        root_item.setExpanded(True)
        dir_items[self.root_path] = root_item
        
        for file_path in sorted(files):
            try:
                rel_path = str(file_path.relative_to(self.root_path))
            except ValueError:
                continue
            
            current_parent = root_item
            for parent in file_path.parents:
                if parent == self.root_path:
                    break
                
                if parent not in dir_items:
                    parent_name = parent.name
                    dir_item = QTreeWidgetItem(current_parent, [f"📁 {parent_name}/", "", "Folder", ""])
                    dir_item.setExpanded(False)
                    dir_items[parent] = dir_item
                
                current_parent = dir_items[parent]
            
            file_size = self.format_size(file_path.stat().st_size)
            file_type = file_path.suffix[1:].upper() if file_path.suffix else "File"
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            
            file_item = QTreeWidgetItem(current_parent, [
                f"📄 {file_path.name}",
                file_size,
                file_type,
                mtime
            ])
            
            file_item.setFlags(file_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            if rel_path in self.existing_files:
                file_item.setCheckState(0, Qt.CheckState.Checked)
            else:
                file_item.setCheckState(0, Qt.CheckState.Unchecked)
            
            file_item.setData(0, Qt.ItemDataRole.UserRole, rel_path)
            self.file_items[rel_path] = file_item
        
        self.update_selection_count()
    
    def format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"
    
    def on_item_changed(self, item, column):
        """Handle item check state change"""
        if column == 0:
            self.update_selection_count()
    
    def update_selection_count(self):
        """Update and emit selection count"""
        count = sum(1 for item in self.file_items.values() 
                   if item.checkState(0) == Qt.CheckState.Checked)
        self.selectionChanged.emit(count)
    
    def get_selected_files(self) -> List[str]:
        """Get list of selected file paths"""
        selected = []
        for rel_path, item in self.file_items.items():
            if item.checkState(0) == Qt.CheckState.Checked:
                selected.append(rel_path)
        return selected
    
    def select_all(self):
        """Select all files"""
        for item in self.file_items.values():
            item.setCheckState(0, Qt.CheckState.Checked)
    
    def deselect_all(self):
        """Deselect all files"""
        for item in self.file_items.values():
            item.setCheckState(0, Qt.CheckState.Unchecked)
    
    def filter_tree(self, search_text: str):
        """Filter tree based on search text"""
        search_text = search_text.lower()
        
        def filter_item(item):
            text = item.text(0).lower()
            matches = search_text in text
            
            has_visible_child = False
            for i in range(item.childCount()):
                child = item.child(i)
                if filter_item(child):
                    has_visible_child = True
            
            should_show = matches or has_visible_child or not search_text
            item.setHidden(not should_show)
            
            return should_show
        
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            filter_item(root.child(i))

class ModernFileSelector(QMainWindow):
    """Modern PyQt6 file selector with smart detection"""
    
    def __init__(self, root_path: Path, existing_files: Set[str]):
        super().__init__()
        self.root_path = root_path
        self.existing_files = existing_files
        self.selected_files = None
        self.detector = SmartFileDetector(root_path)
        
        self.setWindowTitle("verctrl - Smart File Selector")
        self.setGeometry(100, 100, 1000, 700)
        
        self.init_ui()
        self.load_file_tree()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        title = QLabel("Select Files to Track")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        smart_panel = self.create_smart_panel()
        main_layout.addWidget(smart_panel)
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter files...")
        self.search_input.textChanged.connect(self.filter_tree)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size", "Type", "Modified"])
        self.tree.setColumnWidth(0, 400)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 100)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.itemChanged.connect(self.on_item_changed)
        main_layout.addWidget(self.tree)
        button_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setIcon(get_lucide_icon("check", 16, "#4CAF50"))
        self.select_all_btn.clicked.connect(self.select_all)
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.setIcon(get_lucide_icon("x", 16, "#F44336"))
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self.tree.expandAll)
        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self.tree.collapseAll)
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.deselect_all_btn)
        button_layout.addWidget(self.expand_all_btn)
        button_layout.addWidget(self.collapse_all_btn)
        button_layout.addStretch()
        save_btn = QPushButton("Save Selection")
        save_btn.setIcon(get_lucide_icon("save", 16, "#FFFFFF"))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        save_btn.clicked.connect(self.save_selection)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
    
    def create_smart_panel(self):
        """Create smart detection panel"""
        group = QGroupBox("Smart Detection")
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Strategy:"))
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "smart (recommended)",
            "source",
            "recent",
            "python",
            "web",
            "all"
        ])
        layout.addWidget(self.strategy_combo)
        
        layout.addWidget(QLabel("Days:"))
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        layout.addWidget(self.days_spin)
        
        apply_btn = QPushButton("Apply Detection")
        apply_btn.clicked.connect(self.apply_smart_detection)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def apply_smart_detection(self):
        """Apply smart detection strategy"""
        strategy_text = self.strategy_combo.currentText()
        strategy = strategy_text.split()[0]  
        days = self.days_spin.value()
        
        detected = self.detector.detect_files(strategy, days)
        
        if not detected:
            QMessageBox.warning(self, "No Files", "No files detected with this strategy!")
            return
        
        detected_rel = {str(f.relative_to(self.root_path)) for f in detected}
        
        self.check_files_in_tree(detected_rel)
        
        self.status_label.setText(f"Applied {strategy} strategy - {len(detected_rel)} files detected")
    
    def check_files_in_tree(self, file_paths: Set[str]):
        """Check specific files in the tree"""
        def check_recursive(item):
            file_path = item.data(0, Qt.ItemDataRole.UserRole)
            if file_path and file_path in file_paths:
                item.setCheckState(0, Qt.CheckState.Checked)
            
            for i in range(item.childCount()):
                check_recursive(item.child(i))
        
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            check_recursive(root.child(i))
    
    def load_file_tree(self):
        """Load file tree structure"""
        self.tree.clear()
        
        def add_directory(parent_item, directory):
            try:
                items = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            except PermissionError:
                return
            
            for item_path in items:
                if self.detector.should_exclude(item_path):
                    continue
                
                rel_path = str(item_path.relative_to(self.root_path))
                
                if item_path.is_dir():
                    dir_item = QTreeWidgetItem(parent_item)
                    dir_item.setText(0, item_path.name)
                    dir_item.setIcon(0, get_lucide_icon("folder", 16, "#FFA726"))
                    dir_item.setData(0, Qt.ItemDataRole.UserRole, None)
                    dir_item.setFlags(dir_item.flags() | Qt.ItemFlag.ItemIsAutoTristate)
                    add_directory(dir_item, item_path)
                else:
                    file_item = QTreeWidgetItem(parent_item)
                    file_item.setText(0, item_path.name)
                    file_item.setIcon(0, get_file_icon(item_path))
                    file_item.setData(0, Qt.ItemDataRole.UserRole, rel_path)
                    
                    try:
                        size = item_path.stat().st_size
                        if size < 1024:
                            size_str = f"{size} B"
                        elif size < 1024 * 1024:
                            size_str = f"{size / 1024:.1f} KB"
                        else:
                            size_str = f"{size / (1024 * 1024):.1f} MB"
                        file_item.setText(1, size_str)
                    except:
                        file_item.setText(1, "?")
                    
                    file_item.setText(2, item_path.suffix or "file")
                    
                    try:
                        mtime = datetime.fromtimestamp(item_path.stat().st_mtime)
                        file_item.setText(3, mtime.strftime("%Y-%m-%d %H:%M"))
                    except:
                        file_item.setText(3, "?")
                    
                    file_item.setFlags(file_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    
                    if rel_path in self.existing_files:
                        file_item.setCheckState(0, Qt.CheckState.Checked)
                    else:
                        file_item.setCheckState(0, Qt.CheckState.Unchecked)
        
        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, self.root_path.name)
        root_item.setIcon(0, get_lucide_icon("folder-open", 16, "#FF9800"))
        root_item.setExpanded(True)
        
        add_directory(root_item, self.root_path)
        self.update_status()
    
    def filter_tree(self, text):
        """Filter tree items based on search text"""
        def filter_recursive(item):
            visible = False
            file_path = item.data(0, Qt.ItemDataRole.UserRole)
            
            if text.lower() in item.text(0).lower():
                visible = True
            
            for i in range(item.childCount()):
                child_visible = filter_recursive(item.child(i))
                visible = visible or child_visible
            
            item.setHidden(not visible)
            return visible
        
        if not text:
            def show_all(item):
                item.setHidden(False)
                for i in range(item.childCount()):
                    show_all(item.child(i))
            
            root = self.tree.invisibleRootItem()
            for i in range(root.childCount()):
                show_all(root.child(i))
        else:
            root = self.tree.invisibleRootItem()
            for i in range(root.childCount()):
                filter_recursive(root.child(i))
    
    def on_item_changed(self, item, column):
        """Handle item check state change"""
        self.update_status()
    
    def update_status(self):
        """Update status bar with selection count"""
        count = self.count_checked_files()
        self.status_label.setText(f"Selected: {count} file(s)")
    
    def count_checked_files(self):
        """Count checked files in tree"""
        count = 0
        
        def count_recursive(item):
            nonlocal count
            if item.data(0, Qt.ItemDataRole.UserRole) is not None:
                if item.checkState(0) == Qt.CheckState.Checked:
                    count += 1
            
            for i in range(item.childCount()):
                count_recursive(item.child(i))
        
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            count_recursive(root.child(i))
        
        return count
    
    def get_checked_files(self):
        """Get list of checked file paths"""
        files = []
        
        def collect_recursive(item):
            file_path = item.data(0, Qt.ItemDataRole.UserRole)
            if file_path and item.checkState(0) == Qt.CheckState.Checked:
                files.append(file_path)
            
            for i in range(item.childCount()):
                collect_recursive(item.child(i))
        
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            collect_recursive(root.child(i))
        
        return sorted(files)
    
    def select_all(self):
        """Select all visible files"""
        def check_recursive(item):
            if not item.isHidden():
                if item.data(0, Qt.ItemDataRole.UserRole) is not None:
                    item.setCheckState(0, Qt.CheckState.Checked)
                
                for i in range(item.childCount()):
                    check_recursive(item.child(i))
        
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            check_recursive(root.child(i))
    
    def deselect_all(self):
        """Deselect all files"""
        def uncheck_recursive(item):
            if item.data(0, Qt.ItemDataRole.UserRole) is not None:
                item.setCheckState(0, Qt.CheckState.Unchecked)
            
            for i in range(item.childCount()):
                uncheck_recursive(item.child(i))
        
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            uncheck_recursive(root.child(i))
    
    def save_selection(self):
        """Save selected files and close"""
        self.selected_files = self.get_checked_files()
        
        if not self.selected_files:
            reply = QMessageBox.question(
                self,
                "No Files Selected",
                "No files are selected. Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.close()

class VerCtrl:
    DEFAULT_CONFIG = {
        "files": [],
        "backup_dir": ".verctrl_backups",
        "naming_scheme": "version",
        "keep_history": 5,
        "create_new_file": False
    }

    def __init__(self, config_path="verctrl.json"):
        self.config_path = Path(config_path)
        self.config = None

    def load_config(self):
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            print_error(f"Config file '{self.config_path}' not found!")
            print_info("Run 'verctrl --init' to create a default config file.")
            sys.exit(1)

        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            for key in ['files', 'backup_dir', 'naming_scheme']:
                if key not in self.config:
                    print_error(f"Missing required key '{key}' in config file")
                    sys.exit(1)
            
            self.config.setdefault('keep_history', 5)
            self.config.setdefault('create_new_file', False)
            
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in config file: {e}")
            sys.exit(1)

    def init_config(self):
        """Initialize a default config file"""
        if self.config_path.exists():
            response = input(f"Config file '{self.config_path}' already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print_info("Initialization cancelled.")
                return

        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            print_success(f"Created config file: {self.config_path}")
            print_info("Run 'verctrl --select' to choose files with GUI.")
        except Exception as e:
            print_error(f"Failed to create config file: {e}")
            sys.exit(1)

    def gui_select(self):
        """Launch PyQt6 GUI file selector with smart features"""
        if not HAS_PYQT6:
            print_error("PyQt6 is required for GUI mode!")
            print_info("Install with: pip install PyQt6")
            print_info("Falling back to CLI mode...")
            return
        
        if not self.config_path.exists():
            print_warning("Config file not found. Creating default config...")
            self.init_config()
        
        self.load_config()
        
        print_info("Launching PyQt6 GUI file selector...")
        
        try:
            app = QApplication(sys.argv)
            
            app.setStyle('Fusion')
            
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(33, 150, 243))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(33, 150, 243))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            app.setPalette(palette)
            
            existing_files = set(self.config.get('files', []))
            selector = ModernFileSelector(Path.cwd(), existing_files)
            selector.show()
            
            app.exec()
            
            if selector.selected_files is not None:
                self.config['files'] = selector.selected_files
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                
                print_success(f"\n✓ Updated config with {len(selector.selected_files)} file(s):")
                for f in selector.selected_files[:10]: 
                    print(f"  {Colors.CYAN}•{Colors.RESET} {f}")
                if len(selector.selected_files) > 10:
                    print(f"  {Colors.GRAY}... and {len(selector.selected_files) - 10} more{Colors.RESET}")
            else:
                print_info("\nSelection cancelled. Config unchanged.")
        
        except Exception as e:
            print_error(f"GUI error: {e}")
            import traceback
            traceback.print_exc()

    def get_backup_name(self, filepath, backup_dir):
        """Generate backup filename based on naming scheme"""
        filepath = Path(filepath)
        scheme = self.config.get('naming_scheme', 'version')  
        
        if scheme == "version":
            pattern = re.compile(rf"{re.escape(filepath.stem)}-v(\d+){re.escape(filepath.suffix)}")
            versions = []
            for backup in backup_dir.glob(f"{filepath.stem}-v*{filepath.suffix}"):
                match = pattern.match(backup.name)
                if match:
                    versions.append(int(match.group(1)))
            
            next_version = max(versions, default=0) + 1
            return backup_dir / f"{filepath.stem}-v{next_version}{filepath.suffix}"
        
        elif scheme == "timestamp":
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            return backup_dir / f"{filepath.stem}-{timestamp}{filepath.suffix}"
        
        elif scheme == "simple":
            return backup_dir / f"{filepath.stem}-old{filepath.suffix}"
        
        else:
            print_error(f"Unknown naming scheme: {scheme}")
            sys.exit(1)


    def create_backup(self):
        """Create backups of tracked files"""
        self.load_config()
        
        if not self.config['files']:
            print_warning("No files specified in config!")
            print_info("Run 'verctrl --select' to choose files with GUI.")
            return

        backup_dir = Path(self.config['backup_dir'])
        backup_dir.mkdir(parents=True, exist_ok=True)

        backed_up = 0
        for filepath in self.config['files']:
            filepath = Path(filepath)
            
            if not filepath.exists():
                print_warning(f"File not found: {filepath}")
                continue

            try:
                backup_name = self.get_backup_name(filepath, backup_dir)
                shutil.copy2(filepath, backup_name)
                
                file_size = filepath.stat().st_size
                print_success(f"Backed up: {filepath} → {backup_name.name} ({file_size} bytes)")
                backed_up += 1

                if self.config.get('create_new_file', False):
                    filepath.write_text('')
                    print_info(f"Created new empty file: {filepath}")

            except PermissionError:
                print_error(f"Permission denied: {filepath}")
            except Exception as e:
                print_error(f"Failed to backup {filepath}: {e}")

        if backed_up > 0:
            print_success(f"\n{backed_up} file(s) backed up successfully!")
            self.cleanup_old_backups()
        else:
            print_warning("No files were backed up.")

    def cleanup_old_backups(self):
        """Remove old backups beyond keep_history limit"""
        keep_history = self.config.get('keep_history', 5)
        if keep_history <= 0:
            return

        backup_dir = Path(self.config['backup_dir'])
        if not backup_dir.exists():
            return

        for filepath in self.config['files']:
            filepath = Path(filepath)
            
            pattern = f"{filepath.stem}-*{filepath.suffix}"
            backups = sorted(backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
            
            for old_backup in backups[keep_history:]:
                try:
                    old_backup.unlink()
                    print_info(f"Removed old backup: {old_backup.name}")
                except Exception as e:
                    print_warning(f"Failed to remove {old_backup.name}: {e}")

    def list_backups(self):
        """List all backups with details"""
        self.load_config()
        
        backup_dir = Path(self.config['backup_dir'])
        if not backup_dir.exists():
            print_warning("No backup directory found!")
            return

        backups = sorted(backup_dir.glob('*'), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not backups:
            print_warning("No backups found!")
            return

        print(f"\n{Colors.BOLD}Backups in {backup_dir}:{Colors.RESET}\n")
        print(f"{'Filename':<40} {'Size':<12} {'Modified':<20}")
        print("-" * 75)

        for backup in backups:
            if backup.is_file():
                size = backup.stat().st_size
                mtime = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.2f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.2f} MB"
                
                print(f"{Colors.CYAN}{backup.name:<40}{Colors.RESET} {size_str:<12} {mtime}")

        print(f"\n{Colors.BOLD}Total: {len(backups)} backup(s){Colors.RESET}")

    def restore_backup(self, backup_name):
        """Restore a specific backup file"""
        self.load_config()
        
        backup_dir = Path(self.config['backup_dir'])
        backup_path = backup_dir / backup_name
        
        if not backup_path.exists():
            print_error(f"Backup not found: {backup_name}")
            return

        original_file = None
        for tracked_file in self.config['files']:
            tracked_path = Path(tracked_file)
            if tracked_path.stem in backup_name:
                original_file = tracked_path
                break

        if original_file is None:
            print_warning("Could not determine original filename.")
            target = input("Enter target path to restore to: ").strip()
            if not target:
                print_error("Restore cancelled.")
                return
            original_file = Path(target)

        if original_file.exists():
            response = input(f"Overwrite existing file '{original_file}'? (y/N): ")
            if response.lower() != 'y':
                print_info("Restore cancelled.")
                return

        try:
            shutil.copy2(backup_path, original_file)
            print_success(f"Restored: {backup_name} → {original_file}")
        except Exception as e:
            print_error(f"Failed to restore: {e}")

    def smart_add(self, strategy='smart', max_age_days=30):
        """Smart add files based on detection strategy"""
        if not self.config_path.exists():
            print_warning("Config file not found. Creating default config...")
            self.init_config()
        
        self.load_config()
        
        print_info(f"Running smart detection with strategy: {strategy}")
        
        detector = SmartFileDetector(Path.cwd())
        detected_files = detector.detect_files(strategy, max_age_days)
        
        if not detected_files:
            print_warning("No files detected with this strategy!")
            return
        
        detected_rel = [str(f.relative_to(Path.cwd())) for f in detected_files]
        
        print_success(f"\nDetected {len(detected_rel)} file(s):")
        for f in detected_rel[:20]:  
            print(f"  {Colors.CYAN}•{Colors.RESET} {f}")
        if len(detected_rel) > 20:
            print(f"  {Colors.GRAY}... and {len(detected_rel) - 20} more{Colors.RESET}")
        
        response = input(f"\nAdd these {len(detected_rel)} files to tracking? (y/N): ")
        if response.lower() != 'y':
            print_info("Smart add cancelled.")
            return
        
        existing = set(self.config.get('files', []))
        new_files = existing.union(detected_rel)
        
        self.config['files'] = sorted(new_files)
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        added = len(new_files) - len(existing)
        print_success(f"\n✓ Added {added} new file(s) to tracking!")
        print_info(f"Total tracked files: {len(new_files)}")

    def show_stats(self):
        """Show statistics about tracked files and backups"""
        self.load_config()
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 verctrl Statistics{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        tracked_files = self.config.get('files', [])
        print(f"{Colors.CYAN}📁 Tracked Files:{Colors.RESET} {len(tracked_files)}")
        
        if tracked_files:
            extensions = {}
            total_size = 0
            existing_count = 0
            
            for filepath in tracked_files:
                path = Path(filepath)
                if path.exists():
                    existing_count += 1
                    ext = path.suffix or '(no extension)'
                    extensions[ext] = extensions.get(ext, 0) + 1
                    try:
                        total_size += path.stat().st_size
                    except:
                        pass
            
            print(f"{Colors.GREEN}  ✓ Existing:{Colors.RESET} {existing_count}")
            print(f"{Colors.RED}  ✗ Missing:{Colors.RESET} {len(tracked_files) - existing_count}")
            
            if total_size < 1024:
                size_str = f"{total_size} B"
            elif total_size < 1024 * 1024:
                size_str = f"{total_size / 1024:.2f} KB"
            elif total_size < 1024 * 1024 * 1024:
                size_str = f"{total_size / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
            
            print(f"{Colors.CYAN}  Total Size:{Colors.RESET} {size_str}")
            
            if extensions:
                print(f"\n{Colors.CYAN}  Top File Types:{Colors.RESET}")
                sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]
                for ext, count in sorted_exts:
                    print(f"    {ext}: {count}")
        
        backup_dir = Path(self.config['backup_dir'])
        print(f"\n{Colors.CYAN}💾 Backup Directory:{Colors.RESET} {backup_dir}")
        
        if backup_dir.exists():
            backups = list(backup_dir.glob('*'))
            backup_files = [b for b in backups if b.is_file()]
            
            print(f"{Colors.GREEN}  Total Backups:{Colors.RESET} {len(backup_files)}")
            
            if backup_files:
                backup_size = sum(b.stat().st_size for b in backup_files)
                
                if backup_size < 1024:
                    size_str = f"{backup_size} B"
                elif backup_size < 1024 * 1024:
                    size_str = f"{backup_size / 1024:.2f} KB"
                elif backup_size < 1024 * 1024 * 1024:
                    size_str = f"{backup_size / (1024 * 1024):.2f} MB"
                else:
                    size_str = f"{backup_size / (1024 * 1024 * 1024):.2f} GB"
                
                print(f"{Colors.CYAN}  Total Size:{Colors.RESET} {size_str}")
                
                oldest = min(backup_files, key=lambda p: p.stat().st_mtime)
                newest = max(backup_files, key=lambda p: p.stat().st_mtime)
                
                oldest_time = datetime.fromtimestamp(oldest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                newest_time = datetime.fromtimestamp(newest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"{Colors.CYAN}  Oldest:{Colors.RESET} {oldest_time}")
                print(f"{Colors.CYAN}  Newest:{Colors.RESET} {newest_time}")
        else:
            print(f"{Colors.YELLOW}  No backup directory found{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}⚙️  Configuration:{Colors.RESET}")
        print(f"  Naming Scheme: {self.config.get('naming_scheme', 'timestamp')}")
        print(f"  Keep History: {self.config.get('keep_history', 5)}")
        print(f"  Create New File: {self.config.get('create_new_file', False)}")
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="verctrl - Lightweight version control CLI tool with smart features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  verctrl --init                           Initialize config file
  verctrl --select                         PyQt6 GUI file selection with smart detection
  verctrl --smart-add smart                Smart add source files (respects .gitignore)
  verctrl --smart-add python               Add all Python files
  verctrl --smart-add recent --days 7      Add files modified in last 7 days
  verctrl --new                            Create new backup
  verctrl --list                           List all backups
  verctrl --restore file-v1.txt            Restore specific backup
  verctrl --stats                          Show statistics
  verctrl --config custom.json             Use custom config file

Smart Add Strategies:
  smart      Source files respecting .gitignore (recommended)
  source     All source code files
  recent     Recently modified files (use --days)
  python     Python files only
  web        Web-related files (HTML, CSS, JS, etc.)
  all        All non-excluded files
        """
    )

    parser.add_argument('--init', action='store_true', help='Initialize verctrl.json config file')
    parser.add_argument('--select', action='store_true', help='PyQt6 GUI file selection with smart detection')
    parser.add_argument('--smart-add', metavar='STRATEGY', 
                       choices=['smart', 'source', 'recent', 'python', 'web', 'all'],
                       help='Smart add files based on strategy')
    parser.add_argument('--days', type=int, default=30, 
                       help='Days for recent strategy (default: 30)')
    parser.add_argument('--new', action='store_true', help='Create new version (backup files)')
    parser.add_argument('--list', action='store_true', help='List all backups')
    parser.add_argument('--restore', metavar='FILE', help='Restore a specific backup')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--config', metavar='PATH', default='verctrl.json', help='Path to config file')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    verctrl = VerCtrl(args.config)

    try:
        if args.init:
            verctrl.init_config()
        elif args.select:
            verctrl.gui_select()
        elif args.smart_add:
            verctrl.smart_add(args.smart_add, args.days)
        elif args.new:
            verctrl.create_backup()
        elif args.list:
            verctrl.list_backups()
        elif args.restore:
            verctrl.restore_backup(args.restore)
        elif args.stats:
            verctrl.show_stats()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)

if __name__ == "__main__":
    main()