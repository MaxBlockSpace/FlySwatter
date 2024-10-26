import pytest
import asyncio
from ai_trading_bot.core.task import Task

async def sample_task(**kwargs):
    await asyncio.sleep(0.1)
    return kwargs.get('value', 'default')

async def failing_task(**kwargs):
    raise ValueError("Task failed")

@pytest.mark.asyncio
async def test_task_successful_execution():
    task = Task('test_task', sample_task, {'value': 'test'})
    result = await task.execute()
    
    assert result['status'] == 'completed'
    assert result['result'] == 'test'
    assert result['error'] is None

@pytest.mark.asyncio
async def test_task_failure():
    task = Task('failing_task', failing_task)
    result = await task.execute()
    
    assert result['status'] == 'failed'
    assert result['error'] == 'Task failed'
    assert result['result'] is None

@pytest.mark.asyncio
async def test_task_timeout():
    async def slow_task(**kwargs):
        await asyncio.sleep(2)
        return 'done'
    
    task = Task('slow_task', slow_task, timeout=1)
    result = await task.execute()
    
    assert result['status'] == 'timeout'
    assert 'timed out' in result['error']