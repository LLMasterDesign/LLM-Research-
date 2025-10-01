# Τ{Raven} - Production Deployment Guide

Complete guide for deploying Raven to production environments.

---

## Deployment Options

### 1. **Self-Hosted (VPS/Dedicated Server)** ⭐ Recommended
- Full control over infrastructure
- One-time setup cost
- Best for personal/team use

### 2. **Cloud Platforms (AWS/GCP/Azure)**
- Scalable infrastructure
- Pay-as-you-go pricing
- Enterprise-grade reliability

### 3. **Docker Swarm/Kubernetes**
- Container orchestration
- High availability
- Complex but powerful

### 4. **Raspberry Pi / Home Server**
- Low cost, always-on solution
- Perfect for personal projects
- Minimal resource requirements

---

## Prerequisites

### System Requirements

**Minimum:**
- 1 CPU core
- 1GB RAM
- 10GB disk space
- Ubuntu 20.04+ or similar Linux distro

**Recommended:**
- 2 CPU cores
- 2GB RAM
- 20GB disk space
- Ubuntu 22.04 LTS

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- (Optional) Nginx for reverse proxy
- (Optional) Domain name with SSL

---

## Quick Deployment (VPS)

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Create user for Raven (security best practice)
sudo useradd -m -s /bin/bash raven
sudo usermod -aG docker raven
```

### Step 2: Clone Repository

```bash
# Switch to raven user
sudo su - raven

# Clone repository
git clone https://github.com/yourusername/raven.git
cd raven
```

### Step 3: Configure Environment

```bash
# Run setup wizard
./scripts/setup.sh

# Or manually create .env
cp .env.example .env
nano .env
```

**Important variables for production:**
```env
# Set production mode
DEVELOPMENT_MODE=false

# Enable audit logging
AUDIT_LOGGING=true

# Secure database password
POSTGRES_PASSWORD=use_strong_random_password_here

# Set proper rate limits
MAX_REQUESTS_PER_MINUTE=20

# Configure backup paths
BACKUP_PATH=/var/backups/raven
```

### Step 4: Deploy

```bash
# Build and start services
make deploy

# Or manually with docker-compose
docker-compose --profile production up -d
```

### Step 5: Verify Deployment

```bash
# Check service status
make status

# Run health checks
make health

# View logs
make logs

# Test bot
# Send /start to your Telegram bot
```

---

## Production Hardening

### 1. Firewall Configuration

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTPS (if using web interface)
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

# Check status
sudo ufw status
```

### 2. SSL/TLS Setup (Optional - for web interface)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 3. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/raven`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # n8n
    location /n8n/ {
        proxy_pass http://localhost:5678/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Web interface
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/raven /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Monitoring Setup

#### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor Docker containers
docker stats

# Monitor logs
make logs
```

#### Create monitoring script:

Create `scripts/monitor.sh`:
```bash
#!/bin/bash
# Health monitoring script

check_service() {
    if docker-compose ps | grep -q "$1.*Up"; then
        echo "✅ $1 is running"
        return 0
    else
        echo "❌ $1 is down"
        # Send alert (implement your notification method)
        return 1
    fi
}

check_service "raven-bot"
check_service "redis"
check_service "postgres"
```

#### Setup cron job:
```bash
# Edit crontab
crontab -e

# Add monitoring (every 5 minutes)
*/5 * * * * /home/raven/raven/scripts/monitor.sh
```

### 5. Automated Backups

Create `scripts/backup.sh`:
```bash
#!/bin/bash
# Backup script

BACKUP_DIR="/var/backups/raven/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose exec -T postgres pg_dump -U raven raven_db > "$BACKUP_DIR/database.sql"

# Backup .env and configs
cp .env "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"

# Backup logs
cp -r logs "$BACKUP_DIR/"

# Compress
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Keep only last 7 days
find /var/backups/raven -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup complete: $BACKUP_DIR.tar.gz"
```

Setup automated daily backups:
```bash
# Make executable
chmod +x scripts/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /home/raven/raven/scripts/backup.sh
```

### 6. Log Rotation

Create `/etc/logrotate.d/raven`:
```
/home/raven/raven/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 raven raven
    sharedscripts
    postrotate
        docker-compose restart raven-bot
    endscript
}
```

### 7. Security Best Practices

```bash
# Use secrets for sensitive data
docker secret create telegram_token /path/to/token

# Enable Docker security scanning
docker scan raven-telegram-bot

# Update regularly
make stop
git pull
make build
make start

# Monitor security updates
apt list --upgradable
```

---

## Cloud Platform Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.small (or larger)
   - Storage: 20GB
   - Security group: Allow port 22 (SSH)

2. **Connect and Deploy**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   # Follow "Quick Deployment" steps above
   ```

3. **Configure Elastic IP** (optional)
   - Allocate Elastic IP
   - Associate with instance
   - Update DNS if needed

### Google Cloud Platform

```bash
# Create VM instance
gcloud compute instances create raven-bot \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-small \
    --zone=us-central1-a

# SSH and deploy
gcloud compute ssh raven-bot
# Follow deployment steps
```

### DigitalOcean

1. Create Droplet (Ubuntu 22.04, Basic plan)
2. SSH into droplet
3. Follow deployment steps

### Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Create app
heroku create raven-bot

# Add Heroku Postgres
heroku addons:create heroku-postgresql:mini

# Add Heroku Redis
heroku addons:create heroku-redis:mini

# Set config vars
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set ANTHROPIC_API_KEY=your_key

# Deploy
git push heroku main
```

---

## Docker Swarm (High Availability)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml raven

# Scale services
docker service scale raven_raven-bot=3

# Monitor
docker stack services raven
docker stack ps raven
```

---

## Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: raven-bot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: raven-bot
  template:
    metadata:
      labels:
        app: raven-bot
    spec:
      containers:
      - name: bot
        image: raven-telegram-bot:latest
        envFrom:
        - secretRef:
            name: raven-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

Deploy:
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl logs -f deployment/raven-bot
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor resource usage
- Verify backups completed

**Weekly:**
- Review security updates
- Check disk space
- Analyze usage patterns

**Monthly:**
- Update dependencies
- Review and optimize configuration
- Test disaster recovery

### Update Procedure

```bash
# Stop services
make stop

# Backup
./scripts/backup.sh

# Pull updates
git pull

# Rebuild
make build

# Start
make start

# Verify
make health
```

### Disaster Recovery

```bash
# Restore from backup
BACKUP_FILE="/var/backups/raven/20251001_020000.tar.gz"

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/

# Restore database
docker-compose exec -T postgres psql -U raven raven_db < /tmp/backup/database.sql

# Restore configs
cp /tmp/backup/.env .
cp /tmp/backup/docker-compose.yml .

# Restart
make restart
```

---

## Monitoring & Alerts

### Telegram Notifications

Add to your monitoring script:

```bash
send_telegram_alert() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${ADMIN_TELEGRAM_ID}" \
        -d text="🚨 Raven Alert: $message"
}

# Use in monitoring
if ! check_service "raven-bot"; then
    send_telegram_alert "Bot is down! Restarting..."
    make restart
fi
```

### Uptime Monitoring

Use services like:
- UptimeRobot (free)
- Pingdom
- StatusCake
- Custom healthcheck endpoint

---

## Performance Optimization

### Database Optimization

```sql
-- PostgreSQL tuning
-- Add to postgresql.conf

shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Redis Optimization

```bash
# Add to redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Docker Resource Limits

Update `docker-compose.yml`:
```yaml
services:
  raven-bot:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Troubleshooting

### Common Issues

**Bot not starting:**
```bash
# Check logs
docker-compose logs raven-bot

# Check environment
docker-compose exec raven-bot env | grep TOKEN

# Restart
make restart
```

**Database connection errors:**
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U raven -c "SELECT 1"

# Reset database
docker-compose down
docker volume rm raven_postgres-data
docker-compose up -d
```

**High memory usage:**
```bash
# Monitor
docker stats

# Restart services
make restart

# Adjust resource limits in docker-compose.yml
```

---

## Cost Estimation

### Self-Hosted (VPS)

| Provider | Plan | Monthly Cost |
|----------|------|--------------|
| DigitalOcean | 2GB RAM, 1 CPU | $12 |
| Hetzner | CX11 | €4.5 (~$5) |
| AWS Lightsail | 1GB RAM | $5 |
| Linode | Nanode | $5 |

**+ API Costs:**
- Anthropic Claude: $0.00163/1K tokens (input), $0.00551/1K tokens (output)
- Estimated: $5-20/month for moderate use

### Cloud Platform

- AWS EC2 t3.small: ~$15/month
- GCP e2-small: ~$13/month
- Azure B1S: ~$10/month
- + Database/Redis: $10-30/month

---

## Support & Resources

- **Documentation**: See project README files
- **Community**: GitHub Discussions
- **Issues**: GitHub Issues
- **Updates**: Watch repository for updates

---

**Ready to deploy? Start with Quick Deployment! 🚀**
