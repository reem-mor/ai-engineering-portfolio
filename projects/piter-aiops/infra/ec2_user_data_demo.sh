#!/bin/bash
set -euxo pipefail

# --- Docker ---
dnf update -y
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# --- App config (.env) ---
# No AWS_ACCESS_KEY here on purpose: the EC2 instance profile supplies creds.
# Resource IDs + Flask secret only — see docs/aws_credentials.md
cat > /home/ec2-user/.env <<'ENVEOF'
PITER_AWS_REGION=us-east-1
PITER_BEDROCK_KB_ID=RBTJM6NIG9
PITER_BEDROCK_AGENT_ID=HH4YGSLZUE
PITER_BEDROCK_AGENT_ALIAS_ID=O2EM03R4R3
PITER_BEDROCK_MODEL_ARN=arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.amazon.nova-lite-v1:0
PITER_BEDROCK_NUM_RESULTS=5
PITER_BEDROCK_DATA_SOURCE_ID=YICXAB6WOG
PITER_S3_BUCKET=reem-amdocs-ai-artifacts-3331
PITER_S3_PREFIX=projects/piter-aiops/data/sample_documents
PITER_USE_BEDROCK=true
PITER_FLASK_SECRET_KEY=__FLASK_SECRET__
RAG_BACKEND=agent
MAX_UPLOAD_BYTES=5242880
FLASK_ENV=production
ENVEOF
chown ec2-user:ec2-user /home/ec2-user/.env
chmod 600 /home/ec2-user/.env

# --- Pull from ECR and run ---
IMAGE="329597159579.dkr.ecr.us-east-1.amazonaws.com/incident-rag-bedrock:demo"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 329597159579.dkr.ecr.us-east-1.amazonaws.com
docker pull "$IMAGE"
docker run -d \
  --name piter-aiops \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file /home/ec2-user/.env \
  "$IMAGE"
