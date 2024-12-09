import os
import shutil
import time
import psutil
import gc
import glob
from datetime import datetime, timedelta

class CleanupService:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.temp_dirs = ['__pycache__', '.pytest_cache', 'temp', '.temp', 'build', 'dist']
        self.backup_extensions = ['.bak', '_backup', '_old', '_v', 'backup_v']
        self.temp_extensions = ['.pyc', '.pyo', '.pyd', '.log', '.tmp', '.temp']
        self.memory_threshold = 85  # Memory usage threshold (percentage)
        self.max_log_size = 5 * 1024 * 1024  # 5MB
        self.max_db_size = 50 * 1024 * 1024  # 50MB

    def clean_temp_directories(self):
        """Remove temporary directories and their contents"""
        for root, dirs, _ in os.walk(self.project_root):
            for dir_name in dirs:
                if dir_name in self.temp_dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(dir_path)
                        print(f"Removed temporary directory: {dir_path}")
                    except Exception as e:
                        print(f"Error removing {dir_path}: {e}")

    def clean_all_backups_except_latest(self):
        """Remove all backup files except the most recent one"""
        backup_files = []
        
        # Collect all backup files
        for root, _, files in os.walk(self.project_root):
            for file_name in files:
                if any(ext in file_name for ext in self.backup_extensions):
                    file_path = os.path.join(root, file_name)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
        
        # Group backups by base name (without version number)
        backup_groups = {}
        for file_path, mtime in backup_files:
            base_name = self._get_base_name(file_path)
            if base_name not in backup_groups:
                backup_groups[base_name] = []
            backup_groups[base_name].append((file_path, mtime))
        
        # Keep only the latest backup in each group
        for base_name, files in backup_groups.items():
            # Sort by modification time, newest first
            files.sort(key=lambda x: x[1], reverse=True)
            # Delete all except the newest
            for file_path, _ in files[1:]:
                try:
                    os.remove(file_path)
                    print(f"Removed old backup: {file_path}")
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")

    def _get_base_name(self, file_path):
        """Extract base name without version number"""
        file_name = os.path.basename(file_path)
        for ext in self.backup_extensions:
            if ext in file_name:
                return file_name.split(ext)[0]
        return file_name

    def clean_database(self):
        """Clean up old database records and optimize database"""
        try:
            from app_new import app, db, SalesRecord
            with app.app_context():
                # Keep only last 100 records
                records = SalesRecord.query.order_by(SalesRecord.id.desc()).offset(100).all()
                for record in records:
                    db.session.delete(record)
                
                # Commit changes and optimize
                db.session.commit()
                db.session.execute('VACUUM')  # Optimize SQLite database
                print("Cleaned up old database records and optimized database")
        except Exception as e:
            print(f"Error cleaning database: {e}")

    def aggressive_cleanup(self):
        """Perform aggressive cleanup of all unnecessary files"""
        print("Starting aggressive cleanup...")
        
        # Clean all temporary files
        for root, _, files in os.walk(self.project_root):
            for file in files:
                file_path = os.path.join(root, file)
                # Delete temp files
                if any(file.endswith(ext) for ext in self.temp_extensions):
                    try:
                        os.remove(file_path)
                        print(f"Deleted temp file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

        # Clear all empty directories
        for root, dirs, _ in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Check if directory is empty
                        os.rmdir(dir_path)
                        print(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    print(f"Error removing directory {dir_path}: {e}")

    def clear_logs(self):
        """Clear or truncate log files"""
        log_files = glob.glob(os.path.join(self.project_root, '**/*.log'), recursive=True)
        for log_file in log_files:
            try:
                if os.path.getsize(log_file) > self.max_log_size:
                    # Truncate large log files
                    with open(log_file, 'w') as f:
                        f.truncate(0)
                    print(f"Truncated large log file: {log_file}")
            except Exception as e:
                print(f"Error handling log file {log_file}: {e}")

    def optimize_database(self):
        """Optimize database size and performance"""
        try:
            db_path = os.path.join(self.project_root, 'sales_new.db')
            if os.path.exists(db_path) and os.path.getsize(db_path) > self.max_db_size:
                from app_new import app, db, SalesRecord
                with app.app_context():
                    # Keep only recent records
                    old_records = SalesRecord.query.order_by(SalesRecord.id.desc()).offset(50).all()
                    for record in old_records:
                        db.session.delete(record)
                    db.session.commit()
                    
                    # Optimize database file
                    db.session.execute('VACUUM')
                    print("Database optimized and reduced in size")
        except Exception as e:
            print(f"Error optimizing database: {e}")

    def optimize_memory(self):
        """Optimize memory usage"""
        try:
            # Get memory usage
            memory = psutil.Process(os.getpid())
            memory_percent = memory.memory_percent()
            
            if memory_percent > self.memory_threshold:
                # Force garbage collection
                gc.collect()
                
                # Clear Python's file system cache
                gc.collect(2)
                
                print(f"Memory optimization performed. Usage reduced from {memory_percent:.1f}% to {memory.memory_percent():.1f}%")
        except Exception as e:
            print(f"Error optimizing memory: {e}")

    def force_memory_cleanup(self):
        """Force aggressive memory cleanup"""
        try:
            # Get initial memory usage
            memory = psutil.Process(os.getpid())
            initial_memory = memory.memory_percent()
            
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
            
            # Clear Python's file system cache
            gc.collect(2)
            
            # Clear any remaining references
            import sys
            sys.modules.clear()
            
            final_memory = memory.memory_percent()
            print(f"Forced memory cleanup: {initial_memory:.1f}% → {final_memory:.1f}%")
            
        except Exception as e:
            print(f"Error in force memory cleanup: {e}")

    def run_cleanup(self):
        """Run all cleanup operations"""
        print(f"\nStarting cleanup process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
        
        # Get initial memory usage
        memory = psutil.Process(os.getpid())
        initial_memory = memory.memory_percent()
        print(f"Initial memory usage: {initial_memory:.1f}%")
        
        # Run all cleanup operations
        self.clean_temp_directories()
        self.clean_all_backups_except_latest()
        self.clean_database()
        self.aggressive_cleanup()
        self.clear_logs()
        self.optimize_database()
        
        # If memory usage is still high, force cleanup
        if memory.memory_percent() > self.memory_threshold:
            print("Memory usage still high, forcing cleanup...")
            self.force_memory_cleanup()
        
        final_memory = memory.memory_percent()
        print(f"Cleanup completed. Memory usage: {initial_memory:.1f}% → {final_memory:.1f}%\n")

def main():
    cleanup = CleanupService()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()
