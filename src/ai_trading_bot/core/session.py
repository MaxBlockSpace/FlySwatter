import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

class Session:
    def __init__(self, session_type: str = 'regular'):
        self.session_id = str(uuid4())
        self.session_type = session_type
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = 'initialized'
        self.tasks = []
        self.logger = logging.getLogger(f'ai_trading_bot.session.{self.session_id}')

    def start(self) -> None:
        self.start_time = datetime.now()
        self.status = 'running'
        self.logger.info(f"Starting {self.session_type} session {self.session_id}")

    def end(self) -> None:
        self.end_time = datetime.now()
        self.status = 'completed'
        self.logger.info(f"Ending session {self.session_id}")

    def add_task(self, task: Dict[str, Any]) -> None:
        self.tasks.append({
            'timestamp': datetime.now().isoformat(),
            'data': task
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'type': self.session_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'tasks': self.tasks
        }

class SessionManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.session_manager')
        self.active_sessions: Dict[str, Session] = {}
        self.max_concurrent_sessions = 5

    async def start_session(self, session_type: str = 'regular') -> Optional[str]:
        if len(self.active_sessions) >= self.max_concurrent_sessions:
            self.logger.warning("Maximum concurrent sessions reached")
            return None

        session = Session(session_type)
        self.active_sessions[session.session_id] = session
        session.start()
        
        return session.session_id

    async def end_session(self, session_id: str) -> bool:
        if session_id not in self.active_sessions:
            self.logger.warning(f"Session {session_id} not found")
            return False

        session = self.active_sessions[session_id]
        session.end()
        del self.active_sessions[session_id]
        
        return True

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.active_sessions.get(session_id)