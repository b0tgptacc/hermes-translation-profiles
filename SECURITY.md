# Security Policy

## No credentials in Git

This repository must never contain:

- `.env` files;
- API keys, OAuth tokens, cookies, passwords, webhooks, or bearer tokens;
- `auth.json`, `state.db`, sessions, logs, caches, memories, or cron state;
- user source documents or translated business artifacts.

Run before every commit:

```text
python scripts/build_manifest.py
python scripts/verify_repository.py
python -m unittest tests/test_repository.py
```

The verifier reports paths and pattern classes only; it must not print secret values.

## Target-device authentication

Authenticate locally after cloning:

```text
hermes auth add openai-codex
```

Do not add provider credentials to profile specs, `.env.example`, GitHub Actions, or repository secrets unless a separate deployment design explicitly requires them.

## Source documents

Translation files belong in profile workspaces outside the repository. The `.gitignore` excludes common document formats and `inbox/work/output` directories as a second line of defence.

## Reporting

If a credential is committed, revoke or rotate it immediately, remove it from Git history, recreate the sanitized root when necessary, and verify the old credential-bearing SHA is no longer fetchable.
