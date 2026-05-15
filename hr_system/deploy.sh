#!/bin/bash

# HR Management System Deployment Script
# Domain: hrms.agpkacademy.in

echo "🚀 Starting Deployment for HR Management System..."

# 1. Pull latest changes (if using git)
# git pull origin main

# 2. Build and start containers
echo "📦 Building and starting containers..."
docker-compose up -d --build

# 3. Wait for database to be ready
echo "⏳ Waiting for database to initialize..."
sleep 10

# 4. Check status
echo "📊 Container Status:"
docker-compose ps

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at http://hrms.agpkacademy.in"
echo "⚠️  Note: Make sure your DNS A record points to this VPS IP."
echo "⚠️  Note: For SSL, consider using Certbot: docker run -it --rm --name certbot -v \"/etc/letsencrypt:/etc/letsencrypt\" -v \"/var/lib/letsencrypt:/var/lib/letsencrypt\" certbot/certbot certonly --manual -d hrms.agpkacademy.in"
