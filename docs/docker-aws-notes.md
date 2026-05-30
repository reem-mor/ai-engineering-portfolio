# Docker and AWS Notes

Quick reference for container and cloud labs in this repository.

## Docker touchpoints

| Location | What it demonstrates |
|----------|----------------------|
| [`lectures/05_flask_intro/Dockerfile`](../lectures/05_flask_intro/Dockerfile) | Containerize a simple Flask app |
| [`homework/hw04/my-rag-app/`](../homework/hw04/my-rag-app/) | RAG homework Docker starter (app code in progress) |
| [`homework/hw05/nginx-docker-lab/`](../homework/hw05/nginx-docker-lab/) | EC2 + Docker + Nginx evidence and write-up |
| [`projects/incident-assistant-rag/`](../projects/incident-assistant-rag/) | Full-stack Docker Compose (see project README) |

## Homework 05 — EC2 / Docker / Nginx lab

**Handout:** [`resources/handouts/ubuntu-ec2-docker-nginx-student-exercise.docx`](../resources/handouts/ubuntu-ec2-docker-nginx-student-exercise.docx)

**Submission folder:** [`homework/hw05/nginx-docker-lab/`](../homework/hw05/nginx-docker-lab/)

### Lab checklist

1. Launch Ubuntu EC2 (Free Tier eligible where available).
2. Configure Security Group: SSH (22) and HTTP (80).
3. Connect via SSH.
4. Install Docker Engine on Ubuntu.
5. Run Nginx container publishing port 80.
6. Verify welcome page via public IP.
7. Capture screenshots (see lab `screenshots/` folder).
8. Terminate instance when done.

### Screenshot index

Evidence lives in [`homework/hw05/nginx-docker-lab/screenshots/`](../homework/hw05/nginx-docker-lab/screenshots/):

| File | Step |
|------|------|
| `01-ec2-instance-and-security-group.png` | EC2 + SG setup |
| `02-ssh-connection-to-ec2.png` | SSH access |
| `03-docker-installed-and-tested.png` | Docker install |
| `04-docker-run-nginx-container.png` | Nginx container run |
| `05-nginx-container-docker-ps.png` | Container status |
| `06-nginx-welcome-page-browser.png` | Browser validation |
| `07-docker-run-and-cleanup.jpg` | Cleanup |
| `08-ec2-instance-terminating.png` | Instance termination |

## AWS architecture reference

Lecture diagram: [`lectures/07_docker_aws/aws_architecture.mermaid`](../lectures/07_docker_aws/aws_architecture.mermaid)

Slides: [`resources/lecture06_docker_aws.pdf`](../resources/lecture06_docker_aws.pdf)

## Bedrock + Flask project (course guideline)

For the Amazon Bedrock Knowledge Base + Flask + EC2 track, see [`resources/handouts/bedrock-kb-flask-project-guideline.docx`](../resources/handouts/bedrock-kb-flask-project-guideline.docx).

## Security reminders

- Never commit `.pem`, `.key`, or `.env` files (covered by [`.gitignore`](../.gitignore)).
- Rotate any keys that were ever pasted into code or chat logs.
- Terminate EC2 instances after labs to avoid charges.

## Useful commands

```powershell
docker --version
docker ps
docker images
docker build -t my-image .
docker run --rm -p 8080:80 nginx
```
