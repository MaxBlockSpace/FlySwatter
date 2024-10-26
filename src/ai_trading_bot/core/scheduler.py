import logging
import asyncio
from datetime import datetime, time
from typing import Dict, Any, Optional
from .session import Session, SessionManager

class Scheduler:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.core.scheduler')
        self.session_manager = SessionManager()
        self.running = False
        self.regular_schedule = [
            time(9, 0),   # 9:00 AM
            time(13, 0),  # 1:00 PM
            time(17, 0)   # 5:00 PM
        ]
        self.irregular_interval = 4 * 3600  # 4 hours in seconds

    async def start(self) -> None:
        self.running = True
        self.logger.info("Scheduler started")
        
        await asyncio.gather(
            self.schedule_regular_sessions(),
            self.schedule_irregular_sessions()
        )

    async def schedule_regular_sessions(self) -> None:
        while self.running:
            now = datetime.now().time()
            
            for schedule_time in self.regular_schedule:
                if self._should_start_session(now, schedule_time):
                    await self._start_session('regular')
            
            await asyncio.sleep(60)  # Check every minute

    async def schedule_irregular_sessions(self) -> None:
        while self.running:
            await self._start_session('irregular')
            await asyncio.sleep(self.irregular_interval)

    def _should_start_session(self, current: time, scheduled: time) -> bool:
        return (
            current.hour == scheduled.hour and
            current.minute == scheduled.minute
        )

    async def _start_session(self, session_type: str) -> Optional[str]:
        try:
            session_id = await self.session_manager.start_session(session_type)
            if session_id:
                self.logger.info(f"Started {session_type} session {session_id}")
            return session_id
        except Exception as e:
            self.logger.error(f"Failed to start {session_type} session: {e}")
            return None

    def stop(self) -> None:
        self.running = False
        self.logger.info("Scheduler stopped")