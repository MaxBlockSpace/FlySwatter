import pytest
from datetime import datetime, time
from ai_trading_bot.core.scheduler import Scheduler

@pytest.mark.asyncio
async def test_scheduler_initialization():
    scheduler = Scheduler()
    assert not scheduler.running
    assert len(scheduler.sessions) == 0

@pytest.mark.asyncio
async def test_scheduler_start_stop():
    scheduler = Scheduler()
    
    # Start scheduler in background
    task = asyncio.create_task(scheduler.start())
    
    # Let it run briefly
    await asyncio.sleep(0.1)
    
    assert scheduler.running
    
    # Stop scheduler
    scheduler.stop()
    await task
    
    assert not scheduler.running

@pytest.mark.asyncio
async def test_should_start_session():
    scheduler = Scheduler()
    
    # Test exact match
    current = time(9, 0)
    scheduled = time(9, 0)
    assert scheduler._should_start_session(current, scheduled)
    
    # Test non-match
    current = time(9, 1)
    scheduled = time(9, 0)
    assert not scheduler._should_start_session(current, scheduled)