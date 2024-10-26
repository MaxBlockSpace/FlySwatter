import { createLogger } from './utils/logger.js';
import { initializeBot } from './core/initialize.js';

const logger = createLogger('main');

// Initialize error handlers first
window.addEventListener('error', (event) => {
  logger.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled rejection:', event.reason);
});

// Start the bot with proper error handling
try {
  logger.info('Starting AI Trading Bot...');
  await initializeBot();
} catch (error) {
  logger.error('Failed to start bot:', error);
}