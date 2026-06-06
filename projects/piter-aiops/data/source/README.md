# PITER AiOps Source Data

This folder is the canonical location for structured demo and enrichment data.

The files here are copied from the reviewed incoming dataset set and can be
regenerated with:

```bash
python scripts/generate_demo_data.py --output data/source
python scripts/generate_alert_stream.py --output data/source
```

Runtime code still reads the currently verified `data/agent_data` and
`data/sample_documents` folders until the later migration phases prove the
replacement paths preserve the live demo behavior.

Do not store real phone numbers, personal email addresses, credentials, private
keys, or AWS secrets in this folder.
