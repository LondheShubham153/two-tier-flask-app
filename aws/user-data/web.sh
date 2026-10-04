#!/bin/bash
# EC2 user data for Ubuntu Server 24.04 LTS (works on x86_64 and arm64/Graviton).
# Paste this into: Launch template / Launch instance -> Advanced details -> User data.
# EC2 runs it ONCE, as root, on first boot. Output goes to /var/log/user-data.log.
#
# Edit the five values below before you paste it.

DB_HOST="REPLACE_WITH_RDS_ENDPOINT"   # e.g. twotier-db.abc123xyz.ap-south-1.rds.amazonaws.com
DB_NAME="devops"
DB_USER="admin"
DB_PASSWORD="REPLACE_WITH_DB_PASSWORD" # demo only! see "Going further" in aws/README.md
AWS_REGION="ap-south-1"

IMAGE="trainwithshubham/two-tier-flask-app:latest"
LOG_GROUP="/two-tier-flask-app"

exec > >(tee /var/log/user-data.log) 2>&1
set -euxo pipefail

# --- 1. Install Docker from Docker's official apt repository ---
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
# shellcheck source=/dev/null
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
systemctl enable --now docker
usermod -aG docker ubuntu

# --- 2. Run the app ---
# --restart unless-stopped : container comes back after a reboot
# --log-driver awslogs     : container logs go to CloudWatch Logs (needs the IAM role)
docker run -d \
  --name flask-app \
  --restart unless-stopped \
  -p 5000:5000 \
  -e MYSQL_HOST="$DB_HOST" \
  -e MYSQL_USER="$DB_USER" \
  -e MYSQL_PASSWORD="$DB_PASSWORD" \
  -e MYSQL_DB="$DB_NAME" \
  --log-driver awslogs \
  --log-opt awslogs-region="$AWS_REGION" \
  --log-opt awslogs-group="$LOG_GROUP" \
  --log-opt awslogs-create-group=true \
  "$IMAGE"
