#!/bin/bash
# NOCTUA Deployment Script
# Quick deployment helper for NOCTUA system

set -e

echo "═══════════════════════════════════════════════════════════"
echo "🦉 NOCTUA Deployment Script"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION detected"

# Check dependencies
echo ""
echo "🔍 Checking dependencies..."

MISSING_DEPS=()

if ! python3 -c "import tomli" 2>/dev/null && ! python3 -c "import tomllib" 2>/dev/null; then
    MISSING_DEPS+=("tomli")
fi

if ! python3 -c "import redis" 2>/dev/null; then
    echo "⚠️  redis-py not installed (optional)"
fi

if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  flask not installed (optional, needed for dashboard)"
fi

if ! python3 -c "import telegram" 2>/dev/null; then
    echo "⚠️  python-telegram-bot not installed (optional)"
fi

# Install missing critical dependencies
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo ""
    echo "📦 Installing missing dependencies..."
    pip install "${MISSING_DEPS[@]}"
fi

echo ""
echo "🏗️  Building NOCTUA..."
python3 build_noctua.py

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ NOCTUA Deployed Successfully!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📁 Installation: .3ox/"
echo "🦉 Launch: python3 .3ox/owl.py"
echo "🔄 Daemon: python3 .3ox/owl.py --daemon"
echo "🌐 Dashboard: python3 .3ox/dashboard.py"
echo "💬 Telegram: python3 .3ox/telegram_bot.py"
echo ""
echo "📖 Documentation: NOCTUA_README.md"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎯 Quick Commands:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "# Install all features:"
echo "pip install -r requirements.txt"
echo ""
echo "# Start dashboard:"
echo "python3 .3ox/dashboard.py"
echo ""
echo "# Configure Telegram (edit first):"
echo "nano .3ox/config.toml"
echo "python3 .3ox/telegram_bot.py"
echo ""
echo "# Check status:"
echo "cat .3ox/3ox.log"
echo "sqlite3 .3ox/noctua.db 'SELECT COUNT(*) FROM mem'"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🦉 NOCTUA is ready!"
echo "═══════════════════════════════════════════════════════════"
