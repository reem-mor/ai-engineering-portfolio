# 🧹 Cleanup Checklist — Required for Submission

> Execute **every** item below the same day you finish the demo. OpenSearch Serverless and EC2 will continue to bill you until removed. Screenshot the empty consoles for your submission (`10_cleanup_console.png`).

## ✅ Resources to delete (in order)

### 1. EC2
- [ ] **EC2 → Instances** → select `incident-rag-demo` → **Instance state → Terminate**
- [ ] Confirm the attached EBS volume is also deleted (default behaviour)
- [ ] **EC2 → Security Groups** → delete `incident-rag-sg`
- [ ] **EC2 → Key Pairs** → delete the demo key pair if created just for this

### 2. Bedrock Knowledge Base
- [ ] **Bedrock → Knowledge bases** → select `incident-ops-kb` → **Delete**

### 3. OpenSearch Serverless ⚠️ *(the expensive one — easy to forget!)*
- [ ] **OpenSearch → Serverless → Collections** → delete the collection auto-created by the KB
- [ ] **Serverless → Encryption / Network / Data access policies** → delete the policies the KB created

### 4. S3 source bucket
- [ ] **S3 → Buckets** → open `incident-rag-kb-<...>` → **Empty** → then **Delete**

### 5. IAM
- [ ] **IAM → Roles** → delete `incident-rag-ec2-role`
- [ ] **IAM → Roles** → delete the Bedrock-created KB service role (`AmazonBedrockExecutionRoleForKnowledgeBase_…`)
- [ ] **IAM → Policies** → delete any inline / custom policies created above

### 6. Container registry (optional)
- [ ] Delete the GHCR / ECR image if you no longer need it

## 🔎 Verification next day

- [ ] **Billing → Cost Explorer** shows no ongoing Bedrock / OpenSearch / EC2 charges
- [ ] **Bedrock console → Knowledge bases** is empty
- [ ] **OpenSearch Serverless → Collections** is empty
- [ ] **EC2 → Instances** has no running instances in the demo region

## Submission note (what was deleted)

Paste into the README "Cleanup" section:

> All AWS resources created for this project were deleted on **YYYY-MM-DD**:
> EC2 instance `incident-rag-demo` (terminated), security group `incident-rag-sg`,
> Bedrock Knowledge Base `incident-ops-kb`, OpenSearch Serverless collection +
> policies created by the KB, S3 bucket `incident-rag-kb-<...>`, IAM role
> `incident-rag-ec2-role` and the Bedrock-managed KB execution role.
> Cost Explorer confirms no ongoing charges.
