#!/bin/bash

# Exit on any error
set -e

echo "Setting up AI Trading Bot environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data/sessions
mkdir -p data/templates
mkdir -p data/security
mkdir -p data/learning
mkdir -p data/metrics
mkdir -p data/analysis
mkdir -p data/patterns
mkdir -p data/performance
mkdir -p data/community

# Initialize environment file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << EOL
OPENAI_API_KEY=your_openai_api_key
TWITTER_CONSUMER_KEY=your_twitter_consumer_key
TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
ENCRYPTION_KEY=
EOL
    echo "Created .env file - please update with your actual API keys"
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit: AI Trading Bot with learning capabilities"
    echo "Git repository initialized"
fi

echo "Setup complete! Don't forget to:"
echo "1. Update your .env file with actual API keys"
echo "2. Activate the virtual environment with 'source venv/bin/activate'"