#!/bin/bash
# Τ{Raven} - Setup Script
# Automated setup for first-time installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Banner
echo -e "${MAGENTA}"
echo "═══════════════════════════════════════════════"
echo "   Τ{Raven} - Telegram Command Station"
echo "   Automated Setup Script"
echo "═══════════════════════════════════════════════"
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}⚠️  Do not run this script as root${NC}"
   exit 1
fi

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local default="$3"
    local secret="${4:-false}"
    
    if [ "$secret" = "true" ]; then
        read -sp "${prompt} ${default:+[default: hidden]}: " value
        echo
    else
        read -p "${prompt} ${default:+[default: $default]}: " value
    fi
    
    if [ -z "$value" ] && [ -n "$default" ]; then
        value="$default"
    fi
    
    eval "$var_name='$value'"
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 found${NC}"

# Check for Docker (optional)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker not found (optional)${NC}"
    DOCKER_AVAILABLE=false
fi

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️  Git not found (recommended)${NC}"
else
    echo -e "${GREEN}✅ Git found${NC}"
fi

echo ""

# Configuration
echo -e "${BLUE}⚙️  Configuration Setup${NC}"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    prompt_input "Overwrite existing .env? (yes/no)" OVERWRITE "no"
    if [ "$OVERWRITE" != "yes" ]; then
        echo "Keeping existing .env"
        exit 0
    fi
fi

# Telegram Bot Configuration
echo -e "${MAGENTA}━━━ Telegram Bot Configuration ━━━${NC}"
echo "Get your bot token from @BotFather on Telegram"
prompt_input "Telegram Bot Token" TELEGRAM_BOT_TOKEN "" true
echo ""

echo "Get your user ID from @userinfobot on Telegram"
prompt_input "Your Telegram User ID" TELEGRAM_USER_ID
echo ""

prompt_input "Bot Username (without @)" TELEGRAM_BOT_USERNAME
echo ""

# AI Configuration
echo -e "${MAGENTA}━━━ AI Configuration ━━━${NC}"
echo "Get your API key from https://console.anthropic.com/"
prompt_input "Anthropic API Key" ANTHROPIC_API_KEY "" true
echo ""

prompt_input "AI Model" AI_MODEL "claude-sonnet-4"
echo ""

# Workspace Configuration
echo -e "${MAGENTA}━━━ Workspace Configuration ━━━${NC}"
prompt_input "Workspace Path" WORKSPACE_PATH "/workspace"
echo ""

# Database Configuration (optional)
echo -e "${MAGENTA}━━━ Database Configuration (Optional) ━━━${NC}"
prompt_input "Enable PostgreSQL? (yes/no)" ENABLE_POSTGRES "yes"

if [ "$ENABLE_POSTGRES" = "yes" ]; then
    prompt_input "PostgreSQL Password" POSTGRES_PASSWORD "changeme" true
    echo ""
fi

# Security Configuration
echo -e "${MAGENTA}━━━ Security Configuration ━━━${NC}"
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Generated secure secret key"
echo ""

# Create .env file
echo -e "${BLUE}📝 Creating .env file...${NC}"

cat > .env << EOF
# Τ{Raven} - Telegram Command Station Configuration
# Generated: $(date)

# ============================================
# TELEGRAM CONFIGURATION
# ============================================
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_ALLOWED_USERS=${TELEGRAM_USER_ID}
TELEGRAM_BOT_USERNAME=${TELEGRAM_BOT_USERNAME}

# ============================================
# AI CONFIGURATION
# ============================================
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
AI_MODEL=${AI_MODEL}
AI_MAX_TOKENS=4096
AI_TEMPERATURE=0.7

# ============================================
# WORKSPACE CONFIGURATION
# ============================================
WORKSPACE_PATH=${WORKSPACE_PATH}
GIT_REPO_PATH=${WORKSPACE_PATH}
GIT_DEFAULT_BRANCH=main

# ============================================
# DATABASE CONFIGURATION
# ============================================
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

POSTGRES_URL=postgresql://raven:${POSTGRES_PASSWORD}@localhost:5432/raven_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=raven
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=raven_db

# ============================================
# SECURITY SETTINGS
# ============================================
SECRET_KEY=${SECRET_KEY}
MAX_REQUESTS_PER_MINUTE=20
MAX_REQUESTS_PER_HOUR=200
COMMAND_TIMEOUT=300
MAX_FILE_SIZE_MB=10

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/raven.log
AUDIT_LOGGING=true
AUDIT_LOG_FILE=logs/audit.log

# ============================================
# ADVANCED FEATURES
# ============================================
N8N_WEBHOOK_URL=
N8N_API_KEY=
N8N_USER=admin
N8N_PASSWORD=changeme

WEB_INTERFACE_URL=
WEB_INTERFACE_PORT=3000

# ============================================
# DEVELOPMENT SETTINGS
# ============================================
DEVELOPMENT_MODE=false
MOCK_AI_RESPONSES=false
DISABLE_RATE_LIMITING=false
EOF

echo -e "${GREEN}✅ .env file created successfully${NC}"
echo ""

# Create directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p logs
mkdir -p infra/redis
mkdir -p infra/postgres
mkdir -p infra/nginx
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
if [ -f telegram-bot/requirements.txt ]; then
    cd telegram-bot
    pip3 install -r requirements.txt --quiet
    cd ..
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found, skipping${NC}"
fi
echo ""

# Setup complete
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Setup Complete! ✨${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. Start the bot:"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "   ${YELLOW}make start${NC}        # Start with Docker"
    echo "   or"
fi
echo -e "   ${YELLOW}make start-bot${NC}    # Start bot directly"
echo ""

echo "2. Open Telegram and find your bot: @${TELEGRAM_BOT_USERNAME}"
echo ""

echo "3. Send /start to initialize"
echo ""

echo -e "${BLUE}Useful commands:${NC}"
echo -e "   ${YELLOW}make help${NC}         # Show all available commands"
echo -e "   ${YELLOW}make logs${NC}         # View logs"
echo -e "   ${YELLOW}make status${NC}       # Check service status"
echo ""

echo -e "${MAGENTA}Happy coding with Raven! 🚀${NC}"
