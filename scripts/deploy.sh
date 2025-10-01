#!/bin/bash
# Τ{Raven} - Deployment Script
# Deploy to production environment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${MAGENTA}"
echo "═══════════════════════════════════════════════"
echo "   Τ{Raven} - Production Deployment"
echo "═══════════════════════════════════════════════"
echo -e "${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Run ./scripts/setup.sh first"
    exit 1
fi

# Confirm production deployment
echo -e "${YELLOW}⚠️  You are about to deploy to PRODUCTION${NC}"
read -p "Are you sure? (type 'yes' to continue): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo -e "${BLUE}🔍 Pre-deployment checks...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is required for production deployment${NC}"
    exit 1
fi

# Check docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is required${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and docker-compose found${NC}"

# Validate .env
echo -e "${BLUE}🔍 Validating configuration...${NC}"

source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ TELEGRAM_BOT_TOKEN not set${NC}"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ ANTHROPIC_API_KEY not set${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration valid${NC}"

# Backup existing data
if [ -d "data" ]; then
    echo -e "${BLUE}💾 Backing up existing data...${NC}"
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker-compose ps | grep -q postgres; then
        docker-compose exec -T postgres pg_dump -U raven raven_db > "$BACKUP_DIR/database.sql"
        echo -e "${GREEN}✅ Database backed up${NC}"
    fi
    
    # Backup logs
    cp -r logs "$BACKUP_DIR/" 2>/dev/null || true
fi

# Pull latest changes (if in git repo)
if [ -d .git ]; then
    echo -e "${BLUE}📥 Pulling latest changes...${NC}"
    git pull
    echo -e "${GREEN}✅ Code updated${NC}"
fi

# Build Docker images
echo -e "${BLUE}🏗️  Building Docker images...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Build complete${NC}"

# Stop existing services
echo -e "${BLUE}🛑 Stopping existing services...${NC}"
docker-compose down
echo -e "${GREEN}✅ Services stopped${NC}"

# Start services in production mode
echo -e "${BLUE}🚀 Starting services in production mode...${NC}"
docker-compose --profile production up -d

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
sleep 5

# Health checks
echo -e "${BLUE}🏥 Running health checks...${NC}"

# Check bot
if docker-compose exec -T raven-bot python -c "import sys; sys.exit(0)" 2>/dev/null; then
    echo -e "${GREEN}✅ Bot is healthy${NC}"
else
    echo -e "${RED}❌ Bot health check failed${NC}"
    docker-compose logs raven-bot
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Redis health check failed${NC}"
fi

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U raven 2>/dev/null | grep -q "accepting connections"; then
    echo -e "${GREEN}✅ PostgreSQL is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL health check failed${NC}"
fi

# Show service status
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose ps

# Show logs
echo ""
echo -e "${BLUE}📝 Recent logs:${NC}"
docker-compose logs --tail=20

# Deployment complete
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Deployment Complete! ✅${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Monitoring:${NC}"
echo -e "   ${YELLOW}make logs${NC}         # View real-time logs"
echo -e "   ${YELLOW}make status${NC}       # Check service status"
echo -e "   ${YELLOW}make health${NC}       # Run health checks"
echo ""

echo -e "${BLUE}Bot URL:${NC} https://t.me/${TELEGRAM_BOT_USERNAME}"
echo ""

echo -e "${MAGENTA}🎉 Raven is now live in production! 🎉${NC}"
