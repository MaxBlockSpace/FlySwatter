import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from .task import Task

class TaskExecutor:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.core.task_executor')
        self.running_tasks: Dict[str, Task] = {}
        self.max_concurrent_tasks = 10

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        try:
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                raise RuntimeError("Maximum concurrent tasks reached")

            self.running_tasks[task.name] = task
            result = await task.execute()
            del self.running_tasks[task.name]
            
            return result

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            if task.name in self.running_tasks:
                del self.running_tasks[task.name]
            raise

    async def execute_tasks(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        try:
            results = []
            for task in tasks:
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    await self._wait_for_task_slot()
                
                result = await self.execute_task(task)
                results.append(result)
            
            return results

        except Exception as e:
            self.logger.error(f"Tasks execution failed: {e}")
            raise

    async def _wait_for_task_slot(self) -> None:
        while len(self.running_tasks) >= self.max_concurrent_tasks:
            await asyncio.sleep(1)

    def get_running_tasks(self) -> Dict[str, Dict[str, Any]]:
        return {
            task_name: {
                'status': task.status,
                'start_time': task.start_time.isoformat() if task.start_time else None
            }
            for task_name, task in self.running_tasks.items()
        }

    async def cleanup_stale_tasks(self) -> None:
        try:
            current_time = datetime.now()
            stale_tasks = [
                task_name for task_name, task in self.running_tasks.items()
                if task.start_time and (current_time - task.start_time).total_seconds() > 300
            ]
            
            for task_name in stale_tasks:
                await self.cancel_task(task_name)
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup stale tasks: {e}")

    async def cancel_task(self, task_name: str) -> bool:
        try:
            if task_name not in self.running_tasks:
                return False

            task = self.running_tasks[task_name]
            task.status = 'cancelled'
            del self.running_tasks[task_name]
            
            return True

        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_name}: {e}")
            return False