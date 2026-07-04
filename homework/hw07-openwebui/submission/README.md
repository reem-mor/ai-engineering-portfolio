# Submission Evidence

This folder contains evidence for HW07 submission.

## Files

- `QA_INPUT_OUTPUT.md` - human-readable input/output examples and edge cases.
- `evidence.json` - machine-collected evidence from Open WebUI, KB retrieval, tool endpoints, and service checks.
- Screenshots in this folder show local endpoint and setup evidence where automation could capture it.

## Verified State

- Open WebUI `v0.10.2` is healthy on `http://localhost:8080`.
- Tool server is healthy on `http://localhost:5005`.
- Ollama runs directly on Windows host and has `llama3.2:3b` and `nomic-embed-text` installed.
- Open WebUI has:
  - Document: `Netflix Shows KB`
  - Collection: `netflix_shows_kb`
  - Tool: `Netflix Country Info`
  - Prompt: `Netflix HW07 System Prompt`

## Post-Upgrade Evidence

- `QA_AFTER_UPGRADE.md` - final question list and edge-case outputs.
- `edge-case-results-after-upgrade.json` - raw edge-case result data.
- `evidence-after-upgrade.json` - Open WebUI API evidence for runtime models, tool, and prompt.
- `evidence-after-upgrade-db.json` - DB evidence for migrated KB/document/tool/prompt records.
- `final-evidence-host-ollama.json` - final Open WebUI-to-host-Ollama chat smoke test.
- `05-openwebui-knowledge.png` - upgraded Knowledge workspace screenshot.
- `06-openwebui-tools.png` - upgraded Tools workspace screenshot.
- `07-openwebui-prompts.png` - upgraded Prompts workspace screenshot.
- `11-openwebui-models.png` - upgraded Models workspace screenshot.
- `12-edge-atlantis.png` through `16-edge-cote-divoire-after-upgrade.png` - edge-case endpoint screenshots.

## Manual Screenshots Still Recommended

For a polished classroom submission, manually capture these from the browser UI:

- A real chat answer for:
  - `#netflix-shows-kb List Netflix titles from India`
  - `What currency is used in France?`
  - `#netflix-shows-kb Show Netflix titles from Japan and tell me Japan's currency.`

The final source of truth for chat completion is `final-evidence-host-ollama.json`, which verifies Open WebUI can complete a `llama3.2:3b` chat request through host Ollama.

