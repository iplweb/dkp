#!/usr/bin/env python
"""
Daphne Auto-Reloader for macOS
Watches for file changes and automatically restarts Daphne server
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
import threading

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Error: watchdog is not installed.")
    print("Please install it with: pip install watchdog")
    sys.exit(1)


class DaphneReloader(FileSystemEventHandler):
    def __init__(self, command, watch_dirs, ignore_patterns=None):
        self.command = command
        self.watch_dirs = watch_dirs
        self.ignore_patterns = ignore_patterns or [
            '*.pyc', '__pycache__', '.git', '.idea', '*.log',
            '*.sqlite3', 'staticfiles', 'media', 'node_modules',
            '.DS_Store', '*.swp', '*.swo', '*~'
        ]
        self.process = None
        self.restart_lock = threading.RLock()  # Use RLock for reentrant locking
        self.last_restart = 0
        self.restart_delay = 1  # Minimum seconds between restarts

        # Start the initial process
        self.start_process()

    def should_ignore(self, path):
        """Check if the file/directory should be ignored"""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
            if pattern.startswith('*') and path_str.endswith(pattern[1:]):
                return True
        return False

    def on_any_event(self, event):
        """Handle file system events"""
        # Ignore directory events and certain file patterns
        if event.is_directory:
            return

        if self.should_ignore(event.src_path):
            return

        # Only react to Python files and templates
        valid_extensions = ('.py', '.html', '.css', '.js', '.json')
        if not event.src_path.endswith(valid_extensions):
            return

        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_restart < self.restart_delay:
            return

        print(f"\n🔄 Detected change in: {event.src_path}")
        self.restart_process()

    def start_process(self):
        """Start the Daphne process"""
        with self.restart_lock:
            try:
                print(f"🚀 Starting Daphne: {' '.join(self.command)}")
                self.process = subprocess.Popen(
                    self.command,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    preexec_fn=os.setsid  # Create new process group for proper cleanup
                )
                self.last_restart = time.time()
                print(f"✅ Daphne started with PID: {self.process.pid}")
            except Exception as e:
                print(f"❌ Failed to start Daphne: {e}")
                sys.exit(1)

    def stop_process(self):
        """Stop the current Daphne process"""
        if self.process:
            try:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

                # Wait for graceful shutdown (max 5 seconds)
                try:
                    self.process.wait(timeout=5)
                    print("✅ Daphne stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop gracefully
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.wait()
                    print("⚠️ Daphne force stopped")
            except ProcessLookupError:
                # Process already terminated
                pass
            except Exception as e:
                print(f"⚠️ Error stopping Daphne: {e}")

            self.process = None

    def restart_process(self):
        """Restart the Daphne process"""
        with self.restart_lock:
            print("🔄 Restarting Daphne...")
            self.stop_process()
            time.sleep(0.5)  # Brief pause before restart
            self.start_process()


def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python daphne_reloader.py [daphne command and args]")
        print("Example: python daphne_reloader.py daphne dkp.dkp.asgi:application -p 8001")
        sys.exit(1)

    # Get the Daphne command from arguments
    daphne_command = sys.argv[1:]

    # Determine directories to watch
    current_dir = Path.cwd()
    watch_dirs = []

    # Add the dkp directory and its subdirectories
    dkp_dir = current_dir / 'dkp'
    if dkp_dir.exists():
        watch_dirs.append(str(dkp_dir))
    else:
        # Fallback to current directory
        watch_dirs.append(str(current_dir))

    # Create the reloader
    reloader = DaphneReloader(daphne_command, watch_dirs)

    # Set up the file watcher
    observer = Observer()
    for watch_dir in watch_dirs:
        observer.schedule(reloader, watch_dir, recursive=True)
        print(f"👀 Watching directory: {watch_dir}")

    # Start watching
    observer.start()
    print("\n✨ Daphne auto-reloader is running")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
            # Check if process is still running
            if reloader.process and reloader.process.poll() is not None:
                print("\n⚠️ Daphne process died unexpectedly, restarting...")
                reloader.restart_process()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        observer.stop()
        reloader.stop_process()
        observer.join()
        print("👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()