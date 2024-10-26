from setuptools import setup, find_packages

setup(
    name="ai_trading_bot",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "trading-bot=ai_trading_bot.main:main",
        ],
    },
    author="StackBlitz",
    author_email="support@stackblitz.com",
    description="AI Trading Bot for Bitcoin Runes Ecosystem",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stackblitz/ai-trading-bot",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)