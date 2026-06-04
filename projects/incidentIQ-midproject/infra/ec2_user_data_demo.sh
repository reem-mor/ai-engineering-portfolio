#!/bin/bash
set -euxo pipefail

# --- Docker ---
dnf update -y
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# --- App config (.env) ---
# No AWS_ACCESS_KEY here on purpose: the EC2 instance profile supplies creds.
cat > /home/ec2-user/.env <<'ENVEOF'
AWS_REGION=us-east-1
BEDROCK_KB_ID=RBTJM6NIG9
BEDROCK_AGENT_ID=HH4YGSLZUE
BEDROCK_AGENT_ALIAS_ID=O2EM03R4R3
RAG_BACKEND=agent
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.amazon.nova-lite-v1:0
BEDROCK_NUM_RESULTS=5
BEDROCK_DATA_SOURCE_ID=YICXAB6WOG
S3_BUCKET=reem-amdocs-ai-artifacts-3331
S3_PREFIX=projects/incidentIQ-midproject/data/sample_documents
MAX_UPLOAD_BYTES=5242880
FLASK_ENV=production
FLASK_SECRET_KEY=__FLASK_SECRET__
ENVEOF
chown ec2-user:ec2-user /home/ec2-user/.env
chmod 600 /home/ec2-user/.env

# --- Pull from ECR and run ---
IMAGE="329597159579.dkr.ecr.us-east-1.amazonaws.com/incident-rag-bedrock:demo"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 329597159579.dkr.ecr.us-east-1.amazonaws.com
docker pull "$IMAGE"
docker run -d \
  --name incidentiq-midproject \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file /home/ec2-user/.env \
  "$IMAGE"
