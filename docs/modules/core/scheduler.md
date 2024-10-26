# Scheduler

The Scheduler module manages timing and execution of trading sessions.

## Overview

The Scheduler coordinates when trading sessions occur and manages their execution schedule. It provides:

- Regular session scheduling
- Irregular session handling
- Schedule optimization
- Concurrent session management

## Components

### Scheduler Class
- Manages trading schedules
- Coordinates session execution
- Handles timing and intervals

## Usage

```python
# Initialize scheduler
scheduler = Scheduler()

# Start scheduler
scheduler.start()

# Schedule regular sessions
scheduler.schedule_regular_sessions()

# Schedule irregular sessions
scheduler.schedule_irregular_sessions()
```

## Configuration

The scheduler can be configured with:
- Trading hours
- Session intervals
- Concurrency limits
- Market-specific timing