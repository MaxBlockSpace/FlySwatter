import pytest
from datetime import datetime
from ai_trading_bot.core.session import Session

def test_session_initialization():
    session = Session('regular')
    assert session.session_type == 'regular'
    assert session.status == 'initialized'
    assert len(session.tasks) == 0

def test_session_lifecycle():
    session = Session('regular')
    
    session.start()
    assert session.status == 'running'
    assert isinstance(session.start_time, datetime)
    
    session.end()
    assert session.status == 'completed'
    assert isinstance(session.end_time, datetime)

def test_session_task_addition():
    session = Session('regular')
    task = {'type': 'analysis', 'data': 'test'}
    
    session.add_task(task)
    assert len(session.tasks) == 1
    assert session.tasks[0]['data'] == task

def test_session_to_dict():
    session = Session('regular')
    session.start()
    
    task = {'type': 'analysis', 'data': 'test'}
    session.add_task(task)
    
    session_dict = session.to_dict()
    assert session_dict['session_id'] == session.session_id
    assert session_dict['type'] == 'regular'
    assert len(session_dict['tasks']) == 1