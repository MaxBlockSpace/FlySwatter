// Logger utility for consistent logging across the application
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

export class Logger {
  constructor(context) {
    this.context = context;
    this.level = LOG_LEVELS.INFO;
  }

  setLevel(level) {
    this.level = LOG_LEVELS[level] || LOG_LEVELS.INFO;
  }

  format(level, message, ...args) {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] [${this.context}] ${message}`;
  }

  debug(message, ...args) {
    if (this.level <= LOG_LEVELS.DEBUG) {
      console.debug(this.format('DEBUG', message), ...args);
    }
  }

  info(message, ...args) {
    if (this.level <= LOG_LEVELS.INFO) {
      console.info(this.format('INFO', message), ...args);
    }
  }

  warn(message, ...args) {
    if (this.level <= LOG_LEVELS.WARN) {
      console.warn(this.format('WARN', message), ...args);
    }
  }

  error(message, ...args) {
    if (this.level <= LOG_LEVELS.ERROR) {
      console.error(this.format('ERROR', message), ...args);
    }
  }
}

export const createLogger = (context) => {
  return new Logger(context);
};