#!/bin/bash

# ==============================================================================
# 🚀 AUTOMATED VPS DEPLOYMENT & VIRTUAL HOST CONFIGURATION SCRIPT
# Project: Agpk1_HRMS (HR Management System)
# Target Domain: hrms.agpkacademy.in
# Author: Antigravity AI
# ==============================================================================

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Error: Please run this script with sudo or as root."
  exit 1
fi

set -e # Exit immediately if a command exits with a non-zero status

echo "======================================================================"
echo "🌟 Starting HRMS Automated Hostinger VPS Deployment 🌟"
echo "======================================================================"

# Define variables
DOMAIN="hrms.agpkacademy.in"
PROJECT_DIR="$(pwd)"
NGINX_CONF_PATH="/etc/nginx/sites-available/$DOMAIN"
NGINX_ENABLED_PATH="/etc/nginx/sites-enabled/$DOMAIN"

# ------------------------------------------------------------------------------
# STEP 1: Verify Prerequisites
# ------------------------------------------------------------------------------
echo "🔍 Checking system dependencies..."

if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    apt-get update
    apt-get install -y docker-compose-plugin
fi

if ! command -v nginx &> /dev/null; then
    echo "❌ Error: Nginx is not installed on this VPS. Please install Nginx first."
    exit 1
fi

if ! command -v certbot &> /dev/null; then
    echo "📦 Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# ------------------------------------------------------------------------------
# STEP 2: Configure Environment Variables
# ------------------------------------------------------------------------------
echo "📝 Configuring environment files..."

# Generate a secure 64-character SECRET_KEY
JWT_SECRET=$(openssl rand -hex 32)
echo "🔑 Auto-generated a secure JWT Secret Key: $JWT_SECRET"

# Ask user for MongoDB Atlas connection string
echo "----------------------------------------------------------------------"
echo "👉 Please enter your MongoDB Atlas connection string."
echo "Example: mongodb+srv://admin:pass@cluster.mongodb.net/hr_system?retryWrites=true&w=majority"
echo "----------------------------------------------------------------------"
read -p "Connection String: " MONGO_URL

if [ -z "$MONGO_URL" ]; then
    echo "❌ Error: MongoDB URL cannot be empty."
    exit 1
fi

# Write backend/.env
cat <<EOF > "$PROJECT_DIR/backend/.env"
# Application Settings
APP_NAME="HR Management System"
APP_VERSION="1.0.0"
DEBUG=false

# Security
SECRET_KEY="$JWT_SECRET"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
MONGODB_URL="$MONGO_URL"
DATABASE_NAME="hr_system"

# Redis
REDIS_URL="redis://redis:6379"

# CORS
ALLOWED_ORIGINS=["https://$DOMAIN", "http://$DOMAIN"]

# Payroll Default Constants
WORKING_DAYS_PER_MONTH=22
OVERTIME_RATE=1.5
EOF

echo "✅ Environment file created successfully at $PROJECT_DIR/backend/.env"

# ------------------------------------------------------------------------------
# STEP 3: Adjust Docker Compose Ports for Host Coexistence
# ------------------------------------------------------------------------------
# Start scanning for free port from 8080 onwards using python socket checking
PORT=$(python3 -c '
import socket
port = 8080
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", port))
        s.close()
        break
    except socket.error:
        port += 1
print(port)
')

echo "🟢 Found free port: $PORT"

# Update docker-compose.yml to use the discovered free port (supports multiple runs)
python3 -c "import re; f=open('$PROJECT_DIR/docker-compose.yml','r'); content=f.read(); f.close(); content=re.sub(r'- \"\d+:80\"', '- \"$PORT:80\"', content); f=open('$PROJECT_DIR/docker-compose.yml','w'); f.write(content); f.close()"

echo "✅ Port mapping updated in docker-compose.yml to use: Host Port $PORT -> Container Nginx Port 80."

# ------------------------------------------------------------------------------
# STEP 4: Configure Main Host VPS Nginx Virtual Host
# ------------------------------------------------------------------------------
echo "🌐 Setting up Nginx Virtual Host for $DOMAIN..."

cat <<EOF > "$NGINX_CONF_PATH"
server {
    listen 80;
    server_name $DOMAIN;

    # Handle large file uploads (e.g. document management)
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Enable WebSockets support (for hot reloading / socket connections if any)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable the configuration
if [ ! -f "$NGINX_ENABLED_PATH" ]; then
    ln -s "$NGINX_CONF_PATH" "$NGINX_ENABLED_PATH"
fi

# Verify and reload Nginx
echo "🧪 Verifying Nginx configuration syntax..."
nginx -t
echo "🔄 Reloading Nginx server..."
systemctl reload nginx
echo "✅ Host Nginx virtual host configured successfully."

# ------------------------------------------------------------------------------
# STEP 5: Start Docker Containers
# ------------------------------------------------------------------------------
echo "🐳 Launching Docker Containers (building images may take 3-8 minutes)..."
docker compose up -d --build

echo "⏳ Waiting for services to initialize..."
sleep 5

# ------------------------------------------------------------------------------
# STEP 6: SSL Configuration (Let's Encrypt)
# ------------------------------------------------------------------------------
echo "🔒 Requesting Let's Encrypt SSL Certificate..."
certbot --nginx --non-interactive --agree-tos --redirect -m admin@$DOMAIN -d $DOMAIN

echo "======================================================================"
echo "🎉 DEPLOYMENT COMPLETE! 🎉"
echo "======================================================================"
echo "🌐 App URL: https://$DOMAIN"
echo "📊 Containers Health Check:"
docker compose ps
echo "======================================================================"
