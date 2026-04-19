#!/bin/bash

# ==============================================================================
# TaskFlow EC2 Automated Setup Script (Nginx + Gunicorn + Systemd)
# Run this on your EC2 instance with sudo:
# chmod +x setup_ec2.sh
# sudo ./setup_ec2.sh
# ==============================================================================

PROJECT_DIR="$(pwd)"
USER="ubuntu"
GROUP="www-data"

echo "🚀 Starting TaskFlow EC2 Setup..."

# 1. Install prerequisites
echo "📦 Installing prerequisites..."
sudo apt update
sudo apt install -y nginx python3-pip python3-venv python3-dev libmysqlclient-dev default-libmysqlclient-dev build-essential

# 2. Create log and socket directories
echo "📁 Setting up directories..."
sudo mkdir -p /var/log/taskflow /run/taskflow
sudo chown -R $USER:$GROUP /var/log/taskflow /run/taskflow
sudo chmod -R 775 /var/log/taskflow /run/taskflow

# 3. Secure project directory
sudo chown -R $USER:$USER $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

# 4. Create systemd socket unit
echo "⚙️ Creating systemd socket unit..."
sudo cp $PROJECT_DIR/systemd/taskflow.socket /etc/systemd/system/
sudo chown root:root /etc/systemd/system/taskflow.socket

# 5. Create systemd service unit
echo "⚙️ Creating systemd service unit..."
sudo cp $PROJECT_DIR/systemd/taskflow.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/taskflow.service

# 6. Copy Nginx config
echo "🌐 Configuring Nginx..."
sudo cp $PROJECT_DIR/nginx/taskflow.conf /etc/nginx/sites-available/taskflow
sudo ln -sf /etc/nginx/sites-available/taskflow /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 7. Test Nginx config
echo "🔍 Testing Nginx config..."
if sudo nginx -t; then
    echo "✅ Nginx config OK."
else
    echo "❌ Nginx config failed. Exiting."
    exit 1
fi

# 8. Reload and start services
echo "🔄 Reloading systemd and services..."
sudo systemctl daemon-reload
sudo systemctl enable --now taskflow.socket taskflow.service
sudo systemctl restart nginx

echo "✅ Setup complete! TaskFlow should now be accessible via Nginx."
echo "Check status:"
echo "sudo systemctl status taskflow.service nginx"
