#!/usr/bin/env python3
"""
COWN Project Cleanup Script
Removes temporary files, old test results, and cache files
"""

import os
import glob
import shutil
import time
from pathlib import Path

class ProjectCleaner:
    """Clean up COWN project files"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            # Auto-detect project root
            current_dir = Path(__file__).parent.parent
            self.project_root = current_dir
        else:
            self.project_root = Path(project_root)
    
    def clean_python_cache(self):
        """Remove Python cache files"""
        print("🧹 Cleaning Python cache files...")
        
        patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo", 
            "**/*.pyd",
            "**/.pytest_cache",
            "**/.mypy_cache"
        ]
        
        removed_count = 0
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"   📁 Removed directory: {path}")
                    else:
                        path.unlink()
                        print(f"   📄 Removed file: {path}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to remove {path}: {e}")
        
        print(f"   ✅ Removed {removed_count} Python cache items")
    
    def clean_temporary_files(self):
        """Remove temporary files"""
        print("🧹 Cleaning temporary files...")
        
        patterns = [
            "**/*.tmp",
            "**/*.temp", 
            "**/*.bak",
            "**/*.old",
            "**/*~",
            "**/.DS_Store",
            "**/Thumbs.db"
        ]
        
        removed_count = 0
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                try:
                    path.unlink()
                    print(f"   📄 Removed: {path}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to remove {path}: {e}")
        
        print(f"   ✅ Removed {removed_count} temporary files")
    
    def clean_quantum_results(self):
        """Remove old quantum test result files"""
        print("🧹 Cleaning old quantum test results...")
        
        patterns = [
            "**/advanced_qkd_demo_results_*.json",
            "**/quantum_results_*.json",
            "**/cown_quantum_demo_results_*.json",
            "**/qkd_test_results_*.json",
            "**/quantum_benchmark_*.json"
        ]
        
        # Keep files from last 24 hours
        cutoff_time = time.time() - (24 * 60 * 60)
        removed_count = 0
        
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                try:
                    if path.stat().st_mtime < cutoff_time:
                        path.unlink()
                        print(f"   📄 Removed old result: {path}")
                        removed_count += 1
                    else:
                        print(f"   🔒 Keeping recent: {path}")
                except Exception as e:
                    print(f"   ❌ Failed to check {path}: {e}")
        
        print(f"   ✅ Removed {removed_count} old result files")
    
    def clean_logs(self):
        """Remove old log files"""
        print("🧹 Cleaning old log files...")
        
        patterns = [
            "**/*.log",
            "**/logs/*.log",
            "**/log/*.log"
        ]
        
        # Keep logs from last 7 days
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        removed_count = 0
        
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                try:
                    if path.stat().st_mtime < cutoff_time:
                        path.unlink()
                        print(f"   📄 Removed old log: {path}")
                        removed_count += 1
                    else:
                        print(f"   🔒 Keeping recent log: {path}")
                except Exception as e:
                    print(f"   ❌ Failed to check {path}: {e}")
        
        print(f"   ✅ Removed {removed_count} old log files")
    
    def clean_build_artifacts(self):
        """Remove build artifacts"""
        print("🧹 Cleaning build artifacts...")
        
        patterns = [
            "**/dist",
            "**/build", 
            "**/*.egg-info",
            "**/coverage.xml",
            "**/.coverage",
            "**/htmlcov"
        ]
        
        removed_count = 0
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"   📁 Removed directory: {path}")
                    else:
                        path.unlink()
                        print(f"   📄 Removed file: {path}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to remove {path}: {e}")
        
        print(f"   ✅ Removed {removed_count} build artifacts")
    
    def get_project_size(self):
        """Calculate total project size"""
        total_size = 0
        file_count = 0
        
        for path in self.project_root.rglob("*"):
            if path.is_file():
                try:
                    total_size += path.stat().st_size
                    file_count += 1
                except:
                    pass
        
        # Convert to human readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024:
                return f"{total_size:.1f} {unit}", file_count
            total_size /= 1024
        
        return f"{total_size:.1f} TB", file_count
    
    def run_full_cleanup(self):
        """Run complete cleanup process"""
        print("🚀 Starting COWN Project Cleanup")
        print("=" * 50)
        
        # Get initial project size
        initial_size, initial_files = self.get_project_size()
        print(f"📊 Initial project size: {initial_size} ({initial_files} files)")
        print()
        
        # Run cleanup operations
        self.clean_python_cache()
        print()
        
        self.clean_temporary_files()
        print()
        
        self.clean_quantum_results()
        print()
        
        self.clean_logs()
        print()
        
        self.clean_build_artifacts()
        print()
        
        # Get final project size
        final_size, final_files = self.get_project_size()
        print("📊 Cleanup Summary:")
        print(f"   📁 Final project size: {final_size} ({final_files} files)")
        
        print()
        print("🎉 Cleanup completed successfully!")
        print("💡 Tip: Run this script regularly to keep your project clean")

def main():
    """Main cleanup function"""
    cleaner = ProjectCleaner()
    cleaner.run_full_cleanup()

if __name__ == "__main__":
    main()
