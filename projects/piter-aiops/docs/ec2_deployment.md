# EC2 Deployment — Public Demo

Deploy the Dockerized **PITER AiOps** Flask app to a public-facing EC2 instance. Designed for a quick MVP demo, then immediate teardown.

> Legacy names: some EC2/ECR/IAM resources still use `incident-rag-bedrock` or `IncidentRagBedrock*` from the first milestone. New docs and images should prefer `piter-aiops`. Renaming AWS resources is optional and not required for the demo.

> 🔐 **Best practice:** we use an **IAM instance profile** so the container can call Bedrock without any long-lived AWS keys. No `AWS_ACCESS_KEY_ID` ever touches the EC2 instance.

---

## 1. Publish the Docker image

The simplest free option for an MVP is **GitHub Container Registry (GHCR)**:

```bash
# From the project root, after building locally:
docker build -t ghcr.io/<your-gh-user>/piter-aiops:demo .
echo "$GITHUB_TOKEN" | docker login ghcr.io -u <your-gh-user> --password-stdin
docker push ghcr.io/<your-gh-user>/piter-aiops:demo
```

Make the package **public** in GHCR settings so EC2 can pull without authentication.

## 2. Create the IAM role

1. **IAM → Roles → Create role**
   - Trusted entity: **AWS service** → **EC2**
2. Skip the AWS-managed policies for now. Click **Create role**, name it `IncidentRagBedrockEC2Role` (or your chosen name; match the instance profile).
3. After it's created, **Add permissions → Create inline policy → JSON tab**.
4. Paste [`infra/iam_policy.json`](../infra/iam_policy.json), then **replace** the three placeholders:
   - `REGION` → your region (e.g. `us-east-1`)
   - `ACCOUNT_ID` → your 12-digit AWS account ID
   - `KB_ID` → the Knowledge Base ID
   - `S3_BUCKET_NAME` → the bucket holding the runbooks

## 3. Launch the EC2 instance

1. **EC2 → Launch instance**
   - Name: `piter-aiops-demo` (or legacy `incident-rag-demo`)
   - AMI: **Amazon Linux 2023** (free-tier eligible)
   - Instance type: **t3.micro** (or t2.micro)
   - Key pair: create or reuse one — you'll need it for `scp` of the `.env`
2. **Network settings**
   - VPC / Subnet: default
   - Auto-assign public IP: **Enable**
     - Create a **new security group** (e.g. `piter-aiops-sg`):
     - Custom TCP **8080** — Source: `0.0.0.0/0` (app port; matches Docker publish)
     - SSH (22/tcp) — Source: **My IP** (optional)
3. **Advanced details → IAM instance profile**: select `IncidentRagBedrockEC2Profile` (role `IncidentRagBedrockEC2Role`).
4. **User data**: paste [`infra/ec2_user_data_demo.sh`](../infra/ec2_user_data_demo.sh) (ECR `:demo` on port 8080).
5. **Launch**.

📸 *Screenshots*: `04_ec2_instance_running.png`, `05_security_group_rules.png`

## 4. Drop the `.env` file onto the instance

The user-data script expects `/home/ec2-user/.env`. Send it via `scp` once the instance is reachable:

```bash
scp -i <your-key.pem> .env ec2-user@<EC2_PUBLIC_DNS>:/home/ec2-user/.env
ssh -i <your-key.pem> ec2-user@<EC2_PUBLIC_DNS> "sudo systemctl restart docker && sudo docker restart piter-aiops"
```

> ⚠️ The `.env` must **not** contain `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` — the instance profile handles auth.

## 5. Verify

```bash
ssh -i <your-key.pem> ec2-user@<EC2_PUBLIC_DNS> "sudo docker ps"
```
You should see `piter-aiops` (or legacy container name `incident-rag`) with status `Up (healthy)`.

📸 *Screenshot*: `06_docker_ps_on_ec2.png`

Open the app:
```
http://<EC2_PUBLIC_IP>:8080/
```

📸 *Screenshots*: `07_app_homepage_public.png`, `08_app_question_and_answer.png`, `08b_app_citations_expanded.png`, `09_app_refusal_or_low_confidence.png`

## 6. After the demo — TEAR DOWN

See [`cleanup_checklist.md`](cleanup_checklist.md). Do not leave OpenSearch Serverless running.
