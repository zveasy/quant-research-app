#!/bin/bash
set -eux

apt-get update
apt-get install -y ca-certificates curl gnupg git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

useradd -m -s /bin/bash deploy || true
usermod -aG docker deploy

mkdir -p /opt/quant-research
cd /opt/quant-research

git clone https://github.com/YOUR_ORG/quant-research-app.git .
cd quant-research-platform
cp .env.example .env
sed -i 's/your_key_here/REPLACE_ME/' .env

docker compose up -d --build
