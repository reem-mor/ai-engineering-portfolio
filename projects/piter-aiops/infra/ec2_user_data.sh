#!/bin/bash
# EC2 user-data script (Amazon Linux 2023).
# Installs Docker, pulls the public image, runs the container on port 80.
# Replace <IMAGE> with your GHCR / ECR image reference before pasting into the EC2 launch wizard.
set -euxo pipefail

dnf update -y
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# Pull the image (public GHCR by default).
IMAGE="<IMAGE>"   # e.g. ghcr.io/<your-user>/incident-rag-bedrock:demo
docker pull "$IMAGE"

# The .env file with AWS_REGION / BEDROCK_KB_ID / BEDROCK_MODEL_ARN / FLASK_SECRET_KEY
# must already be present at /home/ec2-user/.env (scp it after launch).
# We bind container port 8080 to host port 80 so the app is reachable via http://<public-dns>/.
docker run -d \
  --name incident-rag \
  --restart unless-stopped \
  -p 80:8080 \
  --env-file /home/ec2-user/.env \
  "$IMAGE"
