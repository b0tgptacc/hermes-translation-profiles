# Hermes Translation Profiles

Portable, credential-free deployment package for two Hermes Agent profiles:

- `translator` — complete EN/ZH→RU technical-document translation with local OCR/document tooling, locked-layout PDF reconstruction, glossary support, and fail-closed QA.
- `fasttranslator` — minimal one-call EN/ZH→RU plain-text translation with reasoning disabled and no tools, skills, memory, MCP, or fallback providers.

The repository intentionally contains no `.env`, OAuth data, sessions, state databases, logs, memories, source documents, or translated business artifacts.

## Requirements

1. Hermes Agent installed and available as `hermes`.
2. Python 3.10+.
3. Access to the selected model/provider. The default specs use:

```text
provider: openai-codex
model: gpt-5.6-sol
```

Authenticate separately on every target device:

```text
hermes auth add openai-codex
```

Credentials are never stored in this repository.

## Install

Clone the private repository, then run from its root:

```text
python scripts/install_profiles.py --profiles both --install-deps
```

Default workspaces:

```text
~/Documents/HermesTranslator
~/Documents/HermesFastTranslator
```

Custom workspace root:

```text
python scripts/install_profiles.py --workspace-root D:/HermesWork --profiles both --install-deps
```

Existing profiles are not overwritten. To replace profiles deliberately:

```text
python scripts/install_profiles.py --profiles both --force --install-deps
```

`--force` deletes the existing profiles named `translator` and/or `fasttranslator`. It does not delete existing workspaces.

## Run

Full document profile:

```text
hermes -p translator
```

Fast interactive text profile:

```text
hermes -p fasttranslator --reasoning none
```

Fast file-to-file translation:

Windows:

```text
%USERPROFILE%\Documents\HermesFastTranslator\fasttranslate.bat input.txt output.txt
```

Linux/macOS:

```text
~/Documents/HermesFastTranslator/fasttranslate.sh input.txt output.txt
```

Direct Python:

```text
python ~/Documents/HermesFastTranslator/fasttranslate.py input.txt output.txt
```

## Verify repository before install

```text
python scripts/verify_repository.py
python -m unittest tests/test_repository.py
```

The verifier enforces:

- exact manifest path/size/SHA equality;
- no `.env`, auth, session, database, log, memory, or credential files;
- no private-key, GitHub-token, OpenAI-key, bearer-token, or OAuth-token patterns;
- no machine-specific user Desktop/AppData paths;
- no blobs near GitHub's 100 MB limit;
- two valid profile specs;
- exactly eight vendored translator skills with valid frontmatter.

## Verify installed profiles

```text
hermes profile show translator
hermes profile show fasttranslator
hermes -p translator config check
hermes -p fasttranslator config check
hermes -p translator skills list
hermes -p fasttranslator tools list
```

Then run a live model sentinel after authenticating the provider:

```text
hermes -p fasttranslator --reasoning none -z "Translate into Russian: Hello"
```

Expected: a Russian translation only.

## Uninstall

Profiles only:

```text
python scripts/uninstall_profiles.py --profiles both
```

Profiles and workspaces (destructive):

```text
python scripts/uninstall_profiles.py --profiles both --remove-workspaces
```

## Fonts

The scanned-PDF renderer searches common fonts on Windows, Linux, and macOS. For best Chinese/Cyrillic coverage install Noto Sans CJK or configure explicit paths:

```text
HERMES_TRANSLATION_FONT
HERMES_RU_FONT
HERMES_RU_BOLD_FONT
HERMES_CJK_FONT
```

Font files are not redistributed.

## Repository structure

```text
profiles/
  translator/
    profile-spec.json
    SOUL.md
    workspace.hermes.md
    glossary/
    skills/
  fasttranslator/
    profile-spec.json
    SOUL.md
    fasttranslate.py
scripts/
  install_profiles.py
  uninstall_profiles.py
  build_manifest.py
  verify_repository.py
tests/
  fixtures/
  test_repository.py
MANIFEST.json
```

## What is intentionally excluded

- `.env` and API keys;
- OAuth/auth files;
- Hermes sessions and `state.db`;
- logs, caches, cron, memories, and checkpoints;
- user-provided PDFs/DOCX/PPTX/XLSX;
- generated translations and QA artifacts;
- local virtual environments and runtime binaries.

The standard `hermes profile export` archives are not published because they contain runtime state such as sessions, logs, cache, and `state.db`. This repository instead rebuilds profiles declaratively through the Hermes CLI.
