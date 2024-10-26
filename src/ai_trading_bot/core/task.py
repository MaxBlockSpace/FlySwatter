import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable

class Task:
    def __init__(
        self,
        name: str,
        func: Callable,
        args: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ):
        self.name = name
        self.func = func
        self.args = args or {}
        self.timeout = timeout
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = 'initialized'
        self.result: Optional[Any] = None
        self.error: Optional[Exception] = None
        self.logger = logging.getLogger(f'ai_trading_bot.task.{name}')

    async def execute(self) -> Dict[str, Any]:
        self.start_time = datetime.now()
        self.status = 'running'
        self.logger.info(f"Executing task {self.name}")

        try:
            async with asyncio.timeout(self.timeout):
                self.result = await self.func(**self.args)
                self.status = 'completed'
        except asyncio.TimeoutError:
            self.status = 'timeout'
            self.error = TimeoutError(f"Task {self.name} timed out after {self.timeout} seconds")
            self.logger.error(f"Task timeout: {self.error}")
        except Exception as e:
            self.status = 'failed'
            self.error = e
            self.logger.error(f"Task failed: {e}")
        finally:
            self.end_time = datetime.now()

        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'result': self.result,
            'error': str(self.error) if self.error else None
        }

class TaskExecutor:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.task_executor')
        self.running_tasks: Dict[str, Task] = {}
        self.max_concurrent_tasks = 10

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            raise RuntimeError("Maximum concurrent tasks reached")

        self.running_tasks[task.name] = task
        result = await task.execute()
        del self.running_tasks[task.name]
        
        return result

    def get_task_status(self, task_name: str) -> Optional[Dict[str, Any]]:
        task = self.running_tasks.get(task_name)
        if not task:
            return None

        return task.to_dict()