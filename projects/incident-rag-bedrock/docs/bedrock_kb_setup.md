# Bedrock Knowledge Base — Setup Walkthrough

End-to-end steps to stand up the Knowledge Base that backs the Flask app. All clicks are in the AWS Console; copy IDs into `.env` when you're done.

> 💰 **Cost note:** OpenSearch Serverless (the KB-managed vector store) is **the most expensive** part of this stack. Tear it down the same day — see [`cleanup_checklist.md`](cleanup_checklist.md).

---

## 1. Pick a region

Bedrock model availability varies by region. **`us-east-1`** is the safest default for Claude 3 Haiku + Titan embeddings. Stay in one region for the whole setup.

## 2. Create the S3 bucket for source documents

1. **S3 → Create bucket**
   - Name: `incident-rag-kb-<your-initials>-<yyyymmdd>` (must be globally unique)
   - Region: same as Bedrock (`us-east-1`)
   - Block all public access: ✅ keep enabled
   - Versioning: optional
2. Upload the runbook corpus:
   ```bash
   cd projects/incident-rag-bedrock
   BUCKET=incident-rag-kb-rm-20260601 ./infra/upload_docs_to_s3.sh
   ```
   This syncs documents from `../incident-assistant-rag/data/sample_documents/` into the bucket.

## 3. Enable model access in Bedrock

1. **Bedrock → Model access → Manage model access**
2. Request access for:
   - **Anthropic · Claude 3 Haiku** (used for generation)
   - **Amazon · Titan Text Embeddings V2** (used by the KB)
3. Wait until status = **Access granted** (usually <1 minute).

📸 *Screenshot for submission*: `03_bedrock_model_access_granted.png`

## 4. Create the Knowledge Base

1. **Bedrock → Knowledge bases → Create knowledge base**
2. **Step 1 — Provide details**
   - Name: `incident-ops-kb`
   - Description: *"NOC / SRE runbooks and incident playbooks"*
   - IAM role: **Create and use a new service role** (let Bedrock create one)
3. **Step 2 — Choose data source**
   - Source: **Amazon S3**
   - S3 URI: select the bucket created in step 2
   - Parsing strategy: **Default**
4. **Step 3 — Configure embeddings & vector store**
   - Embeddings model: **Titan Text Embeddings V2**
   - Vector store: **Quick create new vector store → Amazon OpenSearch Serverless** *(recommended for MVP — auto-provisions the collection)*
5. **Step 4 — Review and create**. Wait ~3–5 min for OpenSearch Serverless to provision.

📸 *Screenshot*: `01_bedrock_kb_overview.png`

## 5. Sync the data source

1. Open the KB → **Data source** tab → select the source → click **Sync**.
2. Wait until status = **Available** (a minute or two for ~10 small docs).

📸 *Screenshot*: `02_bedrock_kb_data_source_synced.png`

## 6. Test the KB from the console

In the KB detail page, use **Test knowledge base**:
- Choose the model **Claude 3 Haiku** in the right panel.
- Ask: *"How do I triage an authentication service incident?"*
- You should see an answer plus inline source chunks. ✅

## 7. Capture the IDs and update `.env`

From the KB detail page, copy:
- **Knowledge base ID** → `BEDROCK_KB_ID`
- The full model ARN for Haiku → `BEDROCK_MODEL_ARN`
  (e.g., `arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0`)

Then in `projects/incident-rag-bedrock/`:
```bash
cp .env.example .env
# Edit .env — set AWS_REGION, BEDROCK_KB_ID, BEDROCK_MODEL_ARN, FLASK_SECRET_KEY
```

You're ready to run the app locally — see the top-level `README.md`.
