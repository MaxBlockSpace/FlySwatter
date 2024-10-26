import logging
from typing import Dict, Any, Set
from pathlib import Path
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DirectoryMonitor:
    def __init__(self, root_dir: str = '.'):
        self.logger = logging.getLogger('ai_trading_bot.utils.directory_monitor')
        self.root_dir = Path(root_dir)
        self.observer = Observer()
        self.handler = DirectoryEventHandler()
        self.is_monitoring = False

    async def start_monitoring(self) -> None:
        try:
            self.observer.schedule(
                self.handler,
                str(self.root_dir),
                recursive=True
            )
            self.observer.start()
            self.is_monitoring = True
            self.logger.info("Directory monitoring started")
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            raise

    async def stop_monitoring(self) -> None:
        if self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            self.logger.info("Directory monitoring stopped")

    def get_changes(self) -> Dict[str, Set[str]]:
        return {
            'created': self.handler.created_files,
            'modified': self.handler.modified_files,
            'deleted': self.handler.deleted_files
        }

    def clear_changes(self) -> None:
        self.handler.clear_changes()

class DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.created_files: Set[str] = set()
        self.modified_files: Set[str] = set()
        self.deleted_files: Set[str] = set()
        self.logger = logging.getLogger('ai_trading_bot.utils.directory_handler')

    def on_created(self, event):
        if not event.is_directory:
            self.created_files.add(event.src_path)
            self.logger.info(f"File created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            self.modified_files.add(event.src_path)
            self.logger.info(f"File modified: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            self.deleted_files.add(event.src_path)
            self.logger.info(f"File deleted: {event.src_path}")

    def clear_changes(self):
        self.created_files.clear()
        self.modified_files.clear()
        self.deleted_files.clear()