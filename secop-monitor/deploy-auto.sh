#!/bin/bash

# ============================================
# SECOP Monitor - Automatic Deployment Script
# Run this script on the VPS as: sudo bash deploy-auto.sh
# ============================================

set -e

PROJECT_DIR="/var/www/secop-monitor"
DOMAIN="www.secop.dtgrowthpartners.com"
EMAIL="equipo@dtgrowthpartners.com"
REPO_URL="https://github.com/DTGrowthPartners/Secopll.git"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[*] $1${NC}"; }
print_warning() { echo -e "${YELLOW}[!] $1${NC}"; }
print_error() { echo -e "${RED}[X] $1${NC}"; }
print_info() { echo -e "${BLUE}[i] $1${NC}"; }

clear
echo "=========================================="
echo "   SECOP Monitor - Auto Deployment"
echo "=========================================="
echo ""

# Check if root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root: sudo bash deploy-auto.sh"
    exit 1
fi

print_status "Starting deployment process..."

# Update system
print_status "Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y curl git unzip certbot python3-certbot-nginx ufw docker.io docker-compose-plugin

# Start Docker
print_status "Starting Docker..."
systemctl start docker
systemctl enable docker

# Configure firewall
print_status "Configuring firewall..."
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable

# Create project directory
print_status "Creating project directory..."
mkdir -p $PROJECT_DIR

# Clone from Git if directory is empty
if [ ! -f "$PROJECT_DIR/docker-compose.yml" ] || [ -z "$(ls -A $PROJECT_DIR 2>/dev/null)" ]; then
    print_status "Cloning repository from Git..."
    rm -rf $PROJECT_DIR/*
    git clone $REPO_URL $PROJECT_DIR
fi

# Create .env file
print_status "Creating environment file..."
if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
    cp $PROJECT_DIR/backend/.env.example $PROJECT_DIR/backend/.env
    print_warning "Please edit $PROJECT_DIR/backend/.env and add your API keys"
fi

# Build and start containers
print_status "Building Docker containers (this may take a while)..."
cd $PROJECT_DIR
docker compose build --no-cache

print_status "Starting services..."
docker compose up -d

# Wait for services
print_status "Waiting for services to start..."
sleep 20

# Check services
print_status "Checking services status..."
docker compose ps

# Check if services are running
if ! docker compose ps | grep -q "Up"; then
    print_error "Some services failed to start. Check logs with: docker compose logs"
    docker compose logs
    exit 1
fi

# Get SSL certificate
print_status "Getting SSL certificate..."
certbot certonly --nginx -d $DOMAIN --agree-tos --email $EMAIL --non-interactive || {
    print_warning "SSL certificate could not be obtained. Will retry later."
}

# Copy SSL certificates
if [ -d "/etc/live/$DOMAIN" ]; then
    print_status "Copying SSL certificates..."
    mkdir -p $PROJECT_DIR/nginx/ssl
    cp /etc/live/$DOMAIN/fullchain.pem $PROJECT_DIR/nginx/ssl/
    cp /etc/live/$DOMAIN/privkey.pem $PROJECT_DIR/nginx/ssl/
    chmod 600 $PROJECT_DIR/nginx/ssl/*.pem
else
    print_warning "SSL certificates not found. Using HTTP only."
fi

# Restart nginx
print_status "Restarting services..."
docker compose restart

# Setup SSL auto-renewal
print_status "Setting up SSL auto-renewal..."
echo "0 0 * * * root certbot renew --quiet --deploy-hook 'docker exec secop_nginx nginx -s reload'" > /etc/cron.d/certbot-renew

# Final status
echo ""
echo "=========================================="
print_status "Deployment completed!"
echo "=========================================="
print_info "Your application: https://$DOMAIN"
echo ""
print_info "Useful commands:"
print_info "  - View logs: cd $PROJECT_DIR && docker compose logs -f"
print_info "  - Restart: cd $PROJECT_DIR && docker compose restart"
print_info "  - Stop: cd $PROJECT_DIR && docker compose down"
print_info "  - Rebuild: cd $PROJECT_DIR && docker compose up -d --build"
echo ""
