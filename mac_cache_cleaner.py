#!/usr/bin/env python3
"""
macOS Cache Cleaner
A safe utility to identify and clean large cache directories from ~/Library/
"""

import os
import shutil
import sys
import time
import termios
import tty
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess


class InteractiveUI:
    """Interactive terminal UI for navigating cache directories with arrow keys"""
    
    def __init__(self):
        self.selected_index = 0
        self.items = []
        
    def get_key(self):
        """Get a single keypress from terminal"""
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                
                # Handle escape sequences (arrow keys)
                if key == '\x1b':
                    key += sys.stdin.read(2)
                    
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
            return key
        except Exception:
            # Fallback for non-Unix systems or if termios fails
            return input()

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def move_cursor_up(self, lines):
        """Move cursor up by specified lines"""
        print(f'\033[{lines}A', end='')

    def clear_line(self):
        """Clear current line"""
        print('\033[2K\r', end='')

    def show_menu(self, cache_dirs: List[Tuple[Path, int]], home_dir: Path):
        """Display interactive menu for cache directory selection"""
        self.items = cache_dirs
        deleted_items = set()
        
        while True:
            self.clear_screen()
            
            # Header
            print("🧹 macOS Cache Cleaner - Interactive Mode")
            print("=" * 70)
            print("Use ↑/↓ arrows to navigate, DELETE key to remove item, ESC/Q to quit")
            print("=" * 70)
            
            if not self.items:
                print("\n✅ All cache directories have been cleaned!")
                print("Press any key to exit...")
                self.get_key()
                break
                
            # Calculate total size
            total_size = sum(size for _, size in self.items if _ not in deleted_items)
            total_mb = total_size / (1024 * 1024)
            
            print(f"\n💾 Total remaining cache size: {total_mb:.1f}MB ({total_size:,} bytes)")
            print(f"📊 Showing {len(self.items)} cache directories:\n")
            
            # Display items
            for i, (path, size) in enumerate(self.items):
                size_mb = size / (1024 * 1024)
                
                # Highlight selected item
                if i == self.selected_index:
                    print(f"→ ", end="")
                else:
                    print("  ", end="")
                
                # Show path information
                try:
                    if str(path).startswith(str(home_dir)):
                        rel_path = path.relative_to(home_dir)
                        display_path = f"~/{rel_path}"
                    else:
                        display_path = f"{path} [External]"
                except ValueError:
                    display_path = str(path)
                
                # Color coding for selected item
                if i == self.selected_index:
                    print(f"\033[1;36m{i+1:2d}. {display_path}\033[0m")
                    print(f"    \033[1;36mSize: {size_mb:.1f}MB\033[0m")
                    print(f"    \033[1;36mFull path: {path}\033[0m")
                else:
                    print(f"{i+1:2d}. {display_path}")
                    print(f"    Size: {size_mb:.1f}MB")
                
                print()
            
            print("\n" + "=" * 70)
            print("Controls: ↑/↓ Navigate | DELETE Remove | ESC/Q Quit")
            
            # Get user input
            key = self.get_key()
            
            # Handle key presses
            if key == '\x1b[A':  # Up arrow
                self.selected_index = max(0, self.selected_index - 1)
            elif key == '\x1b[B':  # Down arrow
                self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            elif key == '\x7f' or key.lower() == 'd':  # Delete key or 'd'
                if 0 <= self.selected_index < len(self.items):
                    self._delete_selected_item(home_dir)
            elif key == '\x1b' or key.lower() == 'q':  # Escape or 'q'
                break
            elif key == '\r' or key == '\n':  # Enter - show details
                if 0 <= self.selected_index < len(self.items):
                    self._show_item_details(home_dir)
        
        return []  # Return empty list since we handle deletion in real-time

    def _delete_selected_item(self, home_dir: Path):
        """Delete the currently selected cache directory"""
        if not (0 <= self.selected_index < len(self.items)):
            return
            
        path, size = self.items[self.selected_index]
        size_mb = size / (1024 * 1024)
        
        # Show confirmation
        self.clear_screen()
        print("🗑️  DELETE CONFIRMATION")
        print("=" * 50)
        
        try:
            if str(path).startswith(str(home_dir)):
                rel_path = path.relative_to(home_dir)
                display_path = f"~/{rel_path}"
            else:
                display_path = str(path)
        except ValueError:
            display_path = str(path)
            
        print(f"Directory: {display_path}")
        print(f"Full path: {path}")
        print(f"Size: {size_mb:.1f}MB")
        print("\n🚨 This action cannot be undone!")
        print("\nPress 'Y' to confirm deletion, any other key to cancel...")
        
        confirm_key = self.get_key()
        
        if confirm_key.lower() == 'y':
            try:
                print(f"\nDeleting {display_path}...", end="", flush=True)
                shutil.rmtree(path)
                print(" ✅ Done!")
                
                # Remove from items list
                self.items.pop(self.selected_index)
                
                # Adjust selected index if needed
                if self.selected_index >= len(self.items) and len(self.items) > 0:
                    self.selected_index = len(self.items) - 1
                elif len(self.items) == 0:
                    self.selected_index = 0
                    
                print("\nPress any key to continue...")
                self.get_key()
                
            except Exception as e:
                print(f" ❌ Failed: {str(e)}")
                print("\nPress any key to continue...")
                self.get_key()
        else:
            print("\n🚫 Deletion cancelled.")
            print("Press any key to continue...")
            self.get_key()

    def _show_item_details(self, home_dir: Path):
        """Show detailed information about the selected item"""
        if not (0 <= self.selected_index < len(self.items)):
            return
            
        path, size = self.items[self.selected_index]
        size_mb = size / (1024 * 1024)
        
        self.clear_screen()
        print("📁 DIRECTORY DETAILS")
        print("=" * 50)
        
        try:
            if str(path).startswith(str(home_dir)):
                rel_path = path.relative_to(home_dir)
                print(f"Relative path: ~/{rel_path}")
            else:
                print(f"External cache directory")
        except ValueError:
            print(f"External directory")
            
        print(f"Full path: {path}")
        print(f"Size: {size_mb:.1f}MB ({size:,} bytes)")
        
        # Show modification time if available
        try:
            mtime = path.stat().st_mtime
            mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            print(f"Last modified: {mtime_str}")
        except (OSError, IOError):
            print("Last modified: Unknown")
            
        # Show if it's a node_modules directory
        if path.name == "node_modules":
            print("Type: Node.js project dependencies")
            
            # Try to find package.json in parent directory
            parent_dir = path.parent
            package_json = parent_dir / "package.json"
            if package_json.exists():
                print(f"Project directory: {parent_dir}")
        
        print("\nPress any key to return to menu...")
        self.get_key()


class CacheCleaner:
    def __init__(self):
        self.home_dir = Path.home()
        self.library_dir = self.home_dir / "Library"
        self.min_size_mb = 100
        self.min_days_old = 1  # node_modules must be at least 1 day old
        
        # Safe cache directories to scan (won't touch system-critical areas)
        self.safe_cache_paths = [
            "Caches",
            "Application Support/*/Cache",
            "Application Support/*/Caches", 
            "Logs",
            "WebKit/*/LocalStorage",
            "Safari/LocalStorage",
            "Containers/*/Data/Library/Caches",
            "Group Containers/*/Library/Caches"
        ]
        
        # 3rd party application cache paths (safe to delete)
        self.third_party_caches = [
            # Unity Hub and Unity Editor caches
            "Application Support/Unity/cache",
            "Application Support/Unity Hub/cache",
            "Application Support/Unity/Editor/Cache",
            "Application Support/Unity/Asset Store-5.x",
            "Caches/com.unity3d.UnityEditor5.x",
            "Caches/com.unity3d.unityhub",
            
            # Chrome and Chromium-based browsers
            "Application Support/Google/Chrome/Default/Application Cache",
            "Application Support/Google/Chrome/Default/GPUCache",
            "Application Support/Google/Chrome/Default/ShaderCache",
            "Application Support/Google/Chrome/Profile*/Application Cache",
            "Application Support/Google/Chrome/Profile*/GPUCache",
            "Caches/com.google.Chrome",
            "Caches/com.google.Chrome.helper*",
            
            # Firefox caches
            "Application Support/Firefox/Profiles/*/cache2",
            "Application Support/Firefox/Profiles/*/startupCache",
            "Caches/Firefox",
            
            # VS Code caches
            "Application Support/Code/User/workspaceStorage/*/CachedExtensions*",
            "Application Support/Code/CachedExtensions",
            "Application Support/Code/logs",
            "Caches/com.microsoft.VSCode",
            
            # Xcode caches (safe ones only)
            "Developer/Xcode/DerivedData/*/Build/Intermediates.noindex",
            "Developer/Xcode/DerivedData/*/Index/DataStore",
            "Caches/com.apple.dt.Xcode",
            
            # Slack
            "Application Support/Slack/Service Worker/CacheStorage",
            "Application Support/Slack/Cache",
            "Caches/com.tinyspeck.slackmacgap",
            
            # Discord
            "Application Support/discord/Cache",
            "Application Support/discord/GPUCache",
            "Caches/com.hnc.Discord",
            
            # Spotify
            "Application Support/Spotify/PersistentCache",
            "Caches/com.spotify.client",
            
            # Adobe applications (cache only, not preferences)
            "Application Support/Adobe/Common/Media Cache Files",
            "Application Support/Adobe/*/Cache",
            "Caches/com.adobe.*",
            
            # JetBrains IDEs
            "Application Support/JetBrains/*/system/caches",
            "Application Support/JetBrains/*/system/tmp",
            "Caches/JetBrains",
            
            # Docker
            "Application Support/Docker/Data/vms/0/data/cache",
            "Caches/com.docker.docker",
            
            # Figma
            "Application Support/Figma/DesktopProfile/Default/GPUCache",
            "Caches/com.figma.Desktop"
        ]
        
        # System-critical directories that should NEVER be touched
        self.system_protected = {
            "Keychains", "Preferences", "LaunchAgents", "StartupItems",
            "Services", "PreferencePanes", "PrivateFrameworks", "Frameworks",
            "Developer", "Audio", "ColorSync", "Fonts", "Keyboard Layouts",
            "Printers", "Screen Savers", "Sounds", "Speech", "Spelling",
            "Application Support/com.apple.", "Application Support/Apple",
            "Application Support/MobileSync", "Application Support/SyncServices"
        }

    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        if os.path.exists(filepath) and not os.path.islink(filepath):
                            total_size += os.path.getsize(filepath)
                    except (OSError, IOError):
                        continue
        except (OSError, IOError, PermissionError):
            pass
        return total_size

    def bytes_to_mb(self, bytes_size: int) -> float:
        """Convert bytes to MB"""
        return bytes_size / (1024 * 1024)

    def is_safe_to_delete(self, path: Path) -> bool:
        """Check if path is safe to delete (not system-critical)"""
        try:
            # Handle external caches (outside ~/Library/)
            if not str(path).startswith(str(self.library_dir)):
                return self._is_external_cache_safe(path)
            
            path_str = str(path.relative_to(self.library_dir))
            
            # Check against protected directories
            for protected in self.system_protected:
                if path_str.startswith(protected) or protected in path_str:
                    return False
            
            # Additional safety checks
            if any(critical in path_str.lower() for critical in [
                "system", "kernel", "framework", "daemon", "agent", "loginwindow",
                "windowserver", "coreaudio", "bluetooth", "wifi", "network"
            ]):
                return False
                
            return True
        except ValueError:
            # Path is not relative to library_dir, treat as external
            return self._is_external_cache_safe(path)

    def _is_external_cache_safe(self, path: Path) -> bool:
        """Check if external cache directory is safe to delete"""
        path_str = str(path).lower()
        
        # Safe external cache patterns
        safe_patterns = [
            "/.npm", "/.yarn", "/.cache", "/.composer", "/.gradle/caches",
            "/.m2/repository/.cache", "/.cargo/registry/cache", "/homebrew",
            "/go/pkg/mod/cache", "/cocoapods", "/node_modules"
        ]
        
        # Check if path matches safe patterns
        for pattern in safe_patterns:
            if pattern in path_str:
                return True
        
        # Additional safety: never delete system directories
        unsafe_patterns = [
            "/system", "/usr/bin", "/usr/sbin", "/bin", "/sbin",
            "/etc", "/var/db", "/private", "/applications"
        ]
        
        for unsafe in unsafe_patterns:
            if unsafe in path_str:
                return False
                
        return False  # Conservative: if unsure, don't delete

    def find_cache_directories(self) -> List[Tuple[Path, int]]:
        """Find all cache directories above minimum size threshold"""
        cache_dirs = []
        
        print("🔍 Scanning for cache directories...")
        print(f"   Looking for directories >= {self.min_size_mb}MB")
        print("   Scanning ~/Library/, npm, Homebrew caches, and old node_modules...")
        print("   This may take a few minutes...\n")
        
        # Scan standard Library cache paths
        all_cache_paths = self.safe_cache_paths + self.third_party_caches
        
        for cache_pattern in all_cache_paths:
            pattern_path = self.library_dir / cache_pattern
            
            if "*" in cache_pattern:
                # Handle wildcard patterns
                parent_parts = cache_pattern.split("*")
                if len(parent_parts) >= 2:
                    base_path = self.library_dir / parent_parts[0].rstrip("/")
                    if base_path.exists():
                        try:
                            for item in base_path.iterdir():
                                if item.is_dir():
                                    cache_path = item / parent_parts[1].lstrip("/")
                                    if cache_path.exists() and cache_path.is_dir():
                                        self._check_and_add_cache_dir(cache_path, cache_dirs)
                        except PermissionError:
                            continue
            else:
                # Handle direct paths
                if pattern_path.exists() and pattern_path.is_dir():
                    self._check_and_add_cache_dir(pattern_path, cache_dirs)
        
        # Check npm cache (global)
        self._scan_npm_cache(cache_dirs)
        
        # Check Homebrew cache
        self._scan_homebrew_cache(cache_dirs)
        
        # Check additional system-wide caches
        self._scan_system_caches(cache_dirs)
        
        # Check for old node_modules directories in user projects
        self._scan_node_modules(cache_dirs)
        
        return sorted(cache_dirs, key=lambda x: x[1], reverse=True)

    def _scan_npm_cache(self, cache_dirs: List[Tuple[Path, int]]):
        """Scan npm cache directories"""
        try:
            # Global npm cache
            npm_cache_global = self.home_dir / ".npm"
            if npm_cache_global.exists() and npm_cache_global.is_dir():
                self._check_and_add_external_cache_dir(npm_cache_global, cache_dirs, "npm global cache")
            
            # npm cache in different locations
            possible_npm_caches = [
                self.home_dir / ".npm/_cacache",
                self.home_dir / "Library/Caches/npm",
                Path("/usr/local/lib/node_modules/npm/cache") if Path("/usr/local/lib/node_modules/npm/cache").exists() else None
            ]
            
            for npm_path in possible_npm_caches:
                if npm_path and npm_path.exists() and npm_path.is_dir():
                    self._check_and_add_external_cache_dir(npm_path, cache_dirs, "npm cache")
                    
        except (PermissionError, OSError):
            pass

    def _scan_homebrew_cache(self, cache_dirs: List[Tuple[Path, int]]):
        """Scan Homebrew cache directories"""
        try:
            # Common Homebrew cache locations
            homebrew_caches = [
                Path("/opt/homebrew/var/cache") if Path("/opt/homebrew").exists() else None,  # Apple Silicon
                Path("/usr/local/var/cache") if Path("/usr/local/Homebrew").exists() else None,  # Intel
                self.home_dir / "Library/Caches/Homebrew",
                Path("/tmp/homebrew-cache") if Path("/tmp/homebrew-cache").exists() else None
            ]
            
            for brew_cache in homebrew_caches:
                if brew_cache and brew_cache.exists() and brew_cache.is_dir():
                    self._check_and_add_external_cache_dir(brew_cache, cache_dirs, "Homebrew cache")
                    
        except (PermissionError, OSError):
            pass

    def _scan_system_caches(self, cache_dirs: List[Tuple[Path, int]]):
        """Scan additional system-wide cache locations"""
        try:
            # Additional cache locations
            system_caches = [
                # Yarn cache
                self.home_dir / ".yarn/cache",
                self.home_dir / "Library/Caches/Yarn",
                
                # pip cache
                self.home_dir / ".cache/pip" if (self.home_dir / ".cache/pip").exists() else None,
                self.home_dir / "Library/Caches/pip",
                
                # Composer cache (PHP)
                self.home_dir / ".composer/cache",
                
                # CocoaPods cache
                self.home_dir / "Library/Caches/CocoaPods",
                
                # Gradle cache (safe parts only)
                self.home_dir / ".gradle/caches/modules-2",
                self.home_dir / ".gradle/caches/build-cache-1",
                
                # Maven cache
                self.home_dir / ".m2/repository/.cache",
                
                # Rust cargo cache
                self.home_dir / ".cargo/registry/cache",
                
                # Go module cache
                self.home_dir / "go/pkg/mod/cache" if (self.home_dir / "go/pkg/mod/cache").exists() else None,
            ]
            
            for cache_path in system_caches:
                if cache_path and cache_path.exists() and cache_path.is_dir():
                    self._check_and_add_external_cache_dir(cache_path, cache_dirs, f"{cache_path.parent.name} cache")
                    
        except (PermissionError, OSError):
            pass

    def _scan_node_modules(self, cache_dirs: List[Tuple[Path, int]]):
        """Scan for node_modules directories in user projects that are at least 1 day old"""
        try:
            print("   Scanning for old node_modules directories...")
            
            # Common development directories to scan
            dev_directories = [
                self.home_dir / "Development",
                self.home_dir / "Projects", 
                self.home_dir / "Code",
                self.home_dir / "dev",
                self.home_dir / "projects",
                self.home_dir / "workspace",
                self.home_dir / "Documents" / "Projects",
                self.home_dir / "Documents" / "Development",
                self.home_dir / "Desktop",  # Many people put projects on Desktop
            ]
            
            current_time = time.time()
            one_day_seconds = 24 * 60 * 60
            
            for dev_dir in dev_directories:
                if dev_dir.exists() and dev_dir.is_dir():
                    self._scan_directory_for_node_modules(dev_dir, cache_dirs, current_time, one_day_seconds)
                    
        except (PermissionError, OSError):
            pass

    def _scan_directory_for_node_modules(self, directory: Path, cache_dirs: List[Tuple[Path, int]], current_time: float, one_day_seconds: int, max_depth: int = 4):
        """Recursively scan directory for node_modules, with depth limit to avoid going too deep"""
        if max_depth <= 0:
            return
            
        try:
            for item in directory.iterdir():
                if not item.is_dir():
                    continue
                    
                # Skip hidden directories and common non-project directories
                if item.name.startswith('.') or item.name in ['node_modules', 'dist', 'build', '__pycache__']:
                    continue
                
                # Check if this directory contains node_modules
                node_modules_path = item / "node_modules"
                if node_modules_path.exists() and node_modules_path.is_dir():
                    # Check if node_modules is old enough (at least 1 day)
                    if self._is_node_modules_old_enough(node_modules_path, current_time, one_day_seconds):
                        self._check_and_add_external_cache_dir(node_modules_path, cache_dirs, "node_modules")
                
                # Recursively scan subdirectories (but not too deep)
                if max_depth > 1:
                    self._scan_directory_for_node_modules(item, cache_dirs, current_time, one_day_seconds, max_depth - 1)
                    
        except (PermissionError, OSError):
            pass

    def _is_node_modules_old_enough(self, node_modules_path: Path, current_time: float, one_day_seconds: int) -> bool:
        """Check if node_modules directory hasn't been modified in at least 1 day"""
        try:
            # Check the modification time of the node_modules directory itself
            dir_mtime = node_modules_path.stat().st_mtime
            
            # Also check a few key files/directories inside node_modules that indicate recent activity
            key_paths = [
                node_modules_path / ".package-lock.json",
                node_modules_path / ".yarn-integrity", 
                node_modules_path / ".bin"
            ]
            
            latest_mtime = dir_mtime
            for key_path in key_paths:
                if key_path.exists():
                    key_mtime = key_path.stat().st_mtime
                    latest_mtime = max(latest_mtime, key_mtime)
            
            # Check if it's been at least 1 day since last modification
            age_seconds = current_time - latest_mtime
            return age_seconds >= one_day_seconds
            
        except (OSError, IOError):
            # If we can't determine the age, err on the side of caution
            return False

    def _check_and_add_cache_dir(self, path: Path, cache_dirs: List[Tuple[Path, int]]):
        """Helper method to check and add cache directory if it meets criteria"""
        try:
            if not self.is_safe_to_delete(path):
                return
                
            size = self.get_directory_size(path)
            size_mb = self.bytes_to_mb(size)
            
            if size_mb >= self.min_size_mb:
                cache_dirs.append((path, size))
                print(f"   Found: {path.name} ({size_mb:.1f}MB)")
                
        except (PermissionError, OSError):
            pass

    def _check_and_add_external_cache_dir(self, path: Path, cache_dirs: List[Tuple[Path, int]], cache_type: str):
        """Helper method for external (non-Library) cache directories"""
        try:
            size = self.get_directory_size(path)
            size_mb = self.bytes_to_mb(size)
            
            if size_mb >= self.min_size_mb:
                cache_dirs.append((path, size))
                print(f"   Found: {cache_type} - {path.name} ({size_mb:.1f}MB)")
                
        except (PermissionError, OSError):
            pass

    def display_cache_directories(self, cache_dirs: List[Tuple[Path, int]]) -> Dict[int, Tuple[Path, int]]:
        """Display found cache directories in a numbered list"""
        if not cache_dirs:
            print("✅ No large cache directories found (>= {}MB)".format(self.min_size_mb))
            return {}
        
        print(f"\n📊 Found {len(cache_dirs)} cache directories >= {self.min_size_mb}MB:")
        print("=" * 80)
        
        indexed_dirs = {}
        total_size = 0
        
        for i, (path, size) in enumerate(cache_dirs, 1):
            size_mb = self.bytes_to_mb(size)
            total_size += size
            indexed_dirs[i] = (path, size)
            
            # Show both user-friendly and full path for verification
            try:
                if str(path).startswith(str(self.home_dir)):
                    rel_path = path.relative_to(self.home_dir)
                    print(f"{i:2d}. ~/{rel_path}")
                    print(f"    Full path: {path}")
                else:
                    # External cache - show full path
                    print(f"{i:2d}. {path} [External Cache]")
            except ValueError:
                # Fallback to full path
                print(f"{i:2d}. {path}")
            
            print(f"    Size: {size_mb:.1f}MB")
            print()
        
        total_mb = self.bytes_to_mb(total_size)
        print(f"💾 Total cache size: {total_mb:.1f}MB ({total_size:,} bytes)")
        print("=" * 80)
        
        return indexed_dirs

    def get_user_selection(self, indexed_dirs: Dict[int, Tuple[Path, int]]) -> List[int]:
        """Get user selection for directories to delete"""
        if not indexed_dirs:
            return []
            
        print("\n🗑️  Select directories to delete:")
        print("   Enter numbers separated by spaces (e.g., '1 3 5')")
        print("   Enter 'all' to select all directories")
        print("   Enter 'quit' or 'q' to exit without deleting")
        
        while True:
            try:
                user_input = input("\nYour selection: ").strip().lower()
                
                if user_input in ['quit', 'q', 'exit']:
                    return []
                
                if user_input == 'all':
                    return list(indexed_dirs.keys())
                
                if not user_input:
                    print("❌ Please enter your selection.")
                    continue
                
                # Parse numbers
                selected_nums = []
                for num_str in user_input.split():
                    try:
                        num = int(num_str)
                        if num in indexed_dirs:
                            selected_nums.append(num)
                        else:
                            print(f"❌ Invalid number: {num}")
                            break
                    except ValueError:
                        print(f"❌ Invalid input: {num_str}")
                        break
                else:
                    if selected_nums:
                        return selected_nums
                    else:
                        print("❌ No valid selections made.")
                        
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return []

    def confirm_deletion(self, selected_dirs: List[Tuple[Path, int]]) -> bool:
        """Final confirmation before deletion"""
        if not selected_dirs:
            return False
            
        total_size = sum(size for _, size in selected_dirs)
        total_mb = self.bytes_to_mb(total_size)
        
        print(f"\n⚠️  FINAL CONFIRMATION")
        print(f"   You are about to permanently delete {len(selected_dirs)} directories")
        print(f"   Total size: {total_mb:.1f}MB")
        print("\n📁 Directories to delete:")
        
        for path, size in selected_dirs:
            size_mb = self.bytes_to_mb(size)
            try:
                if str(path).startswith(str(self.home_dir)):
                    rel_path = path.relative_to(self.home_dir)
                    print(f"   • ~/{rel_path}")
                    print(f"     Full path: {path} ({size_mb:.1f}MB)")
                else:
                    print(f"   • {path} [External Cache] ({size_mb:.1f}MB)")
            except ValueError:
                print(f"   • {path} ({size_mb:.1f}MB)")
        
        print(f"\n🚨 THIS ACTION CANNOT BE UNDONE!")
        
        while True:
            confirm = input("\nType 'DELETE' (in capitals) to proceed, or anything else to cancel: ").strip()
            if confirm == 'DELETE':
                return True
            elif confirm:
                return False
            else:
                print("❌ Please enter your choice.")

    def delete_directories(self, selected_dirs: List[Tuple[Path, int]]):
        """Delete selected directories"""
        deleted_count = 0
        deleted_size = 0
        failed_deletions = []
        
        print(f"\n🗑️  Deleting {len(selected_dirs)} directories...")
        
        for path, size in selected_dirs:
            size_mb = self.bytes_to_mb(size)
            
            try:
                # Display path appropriately
                if str(path).startswith(str(self.home_dir)):
                    rel_path = path.relative_to(self.home_dir)
                    display_path = f"~/{rel_path}"
                else:
                    display_path = str(path)
                    rel_path = path  # For error reporting
                
                print(f"   Deleting {display_path}... ", end="", flush=True)
                shutil.rmtree(path)
                print("✅ Done")
                deleted_count += 1
                deleted_size += size
                
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
                failed_deletions.append((display_path, str(e)))
        
        # Summary
        deleted_mb = self.bytes_to_mb(deleted_size)
        print(f"\n📊 Deletion Summary:")
        print(f"   ✅ Successfully deleted: {deleted_count} directories ({deleted_mb:.1f}MB)")
        
        if failed_deletions:
            print(f"   ❌ Failed deletions: {len(failed_deletions)}")
            for path, error in failed_deletions:
                print(f"      • {path}: {error}")

    def choose_interface_mode(self):
        """Let user choose between interactive and classic interface"""
        print("🧹 macOS Cache Cleaner")
        print("=" * 70)
        print("Safely identifies and removes large cache directories from:")
        print("• ~/Library/ (system and app caches)")
        print("• 3rd party apps (Unity, Chrome, VS Code, etc.)")
        print("• Development tools (npm, Homebrew, pip, etc.)")
        print("• Old node_modules in projects (1+ day old only)")
        print("System-critical files are automatically protected.\n")
        
        print("Choose interface mode:")
        print("1. 🖱️  Interactive Mode (arrow keys, delete with DELETE key)")
        print("2. 📝 Classic Mode (numbered selection)")
        
        while True:
            try:
                choice = input("\nEnter your choice (1 or 2): ").strip()
                if choice == '1':
                    return 'interactive'
                elif choice == '2':
                    return 'classic'
                else:
                    print("❌ Please enter 1 or 2")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return None

    def run_interactive_mode(self):
        """Run the interactive arrow-key interface"""
        try:
            # Find cache directories
            cache_dirs = self.find_cache_directories()
            
            if not cache_dirs:
                print("\n✅ No large cache directories found!")
                print("Your system is already clean! 🎉")
                input("\nPress Enter to exit...")
                return
            
            # Launch interactive UI
            ui = InteractiveUI()
            ui.show_menu(cache_dirs, self.home_dir)
            
            print("\n✨ Interactive cleaning session completed!")
            
        except KeyboardInterrupt:
            print("\n\n🚫 Operation cancelled by user. Goodbye!")
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Your files are safe - no deletions were performed.")

    def run_classic_mode(self):
        """Run the classic numbered selection interface"""
        try:
            # Find cache directories
            cache_dirs = self.find_cache_directories()
            
            # Display findings
            indexed_dirs = self.display_cache_directories(cache_dirs)
            
            if not indexed_dirs:
                print("\n👍 Your system is already clean!")
                return
            
            # Get user selection
            selected_numbers = self.get_user_selection(indexed_dirs)
            
            if not selected_numbers:
                print("\n👋 No directories selected. Goodbye!")
                return
            
            # Prepare selected directories for deletion
            selected_dirs = [indexed_dirs[num] for num in selected_numbers]
            
            # Final confirmation
            if not self.confirm_deletion(selected_dirs):
                print("\n🚫 Deletion cancelled. Your files are safe!")
                return
            
            # Delete selected directories
            self.delete_directories(selected_dirs)
            
            print("\n✨ Cache cleaning completed!")
            
        except KeyboardInterrupt:
            print("\n\n🚫 Operation cancelled by user. Goodbye!")
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Your files are safe - no deletions were performed.")

    def run(self):
        """Main execution method"""
        mode = self.choose_interface_mode()
        
        if mode == 'interactive':
            self.run_interactive_mode()
        elif mode == 'classic':
            self.run_classic_mode()
        else:
            print("👋 Goodbye!")
            return


if __name__ == "__main__":
    cleaner = CacheCleaner()
    cleaner.run()
