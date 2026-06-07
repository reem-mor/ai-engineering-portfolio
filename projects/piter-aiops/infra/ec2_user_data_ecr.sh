#!/bin/bash
set -euxo pipefail
dnf update -y
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user
IMAGE="329597159579.dkr.ecr.us-east-1.amazonaws.com/incident-rag-bedrock:demo"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 329597159579.dkr.ecr.us-east-1.amazonaws.com
docker pull "$IMAGE"
docker run -d \
  --name incident-rag \
  --restart unless-stopped \
  -p 80:8080 \
  --env-file /home/ec2-user/.env \
  "$IMAGE"
