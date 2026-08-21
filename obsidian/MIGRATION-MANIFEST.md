---
title: Unified SheperD Environment Migration Manifest
tags:
  - system/migration
  - system/audit
status: complete
---

# Unified SheperD Environment Migration Manifest

This manifest records the approved repository/vault migration. It contains no credentials.

## Current root-layout migration — 2026-08-20

`obsidian/` is the canonical Obsidian vault and contains vault content only.
Application projects are root siblings:

| Current path | Final path | Scope |
| --- | --- | --- |
| `obsidian/founder-intelligence/` | `founder-intelligence/` | tracked and user-created source files; rebuild ignored dependencies |
| `obsidian/recovery/` | `recovery/` | tracked and user-created source files |
| `obsidian/research-agents/` | `research-agents/` | Python source, migrations, tests, config, lockfile |
| `obsidian/website/` | `website/` | tracked and user-created source files; rebuild ignored dependencies |

Root exceptions remain `.git/`, `.gitignore`, `.env.local`, `.claude/`,
`.codegraph/`, `.codex/`, and `.cursor/`.

Pre-move checks:

- Branch: `feat/research-agents-neon`.
- Destination collisions: none for the four final project paths.
- Source files mapped outside approved ignored caches: 525.
- No source symlinks found; symlinks inside ignored `node_modules/` are not source files.
- Existing dirty work is user-owned and preserved.

Post-move verification:

- Destination collision check: passed before the move.
- Destination tree/hash check: passed for the moved source trees; no source file
  was overwritten and Git reports the move as renames/deletes plus the preserved
  pre-existing dirty changes.
- Old project roots: absent (`obsidian/founder-intelligence/`,
  `obsidian/recovery/`, `obsidian/research-agents/`, `obsidian/website/`).
- Generated index: rebuilt from `obsidian/` (`95 files`, `971 chunks`, `1200 terms`).
- Dependencies: rebuilt at the root-sibling project paths only.
- Compatibility symlinks: none created.
- Secret source: root `.env.local` only; values are not recorded here.

Current destination tree inventory (SHA-256 over sorted relative-file SHA-256
records; ignored dependency/build caches, generated Next files, and QA/capture
artifacts excluded):

| Destination | Files | Tree SHA-256 |
| --- | ---: | --- |
| `founder-intelligence/` | 92 | `a49608f2e2f4990347e323f1c12e82e84a1c060845d516d9aa1a79e7761bc444` |
| `recovery/` | 2 | `fa1b0c3709b3e02e159349ed831ddba1acb49aa9b7b7584b0ab0c7e1929a9ee8` |
| `research-agents/` | 39 | `46332090c8f34ba7e4c86a417ee632fdfbc810e3b119beca0d10f4e35345039f` |
| `website/` | 268 | `401795609e2b65f86b0b08be46ac960c139f4aad777cfca2c01699e1590b94d8` |

## Historical destination

- Repository: `feat/research-agents-neon`
- Vault root: `obsidian/`
- Root environment: `.env.local`

## Approved source roots

The following source/content roots move under `obsidian/`:

- `00_System/`
- `01_Company/`
- `02_Domain/`
- `03_GTM/`
- `04_Operations/`
- `05_AI/`
- `06_Goals/`
- `06_Research/`
- `07_Founder_Operating_System/`
- `10_Sources/`
- `90_Templates/`
- `99_Archive/`
- `context/`
- Application projects are now root siblings of `obsidian/`; they are not vault content.
- `OPEN-DESIGN-REBUILD-GOAL.md`
- `README.md`
- `SheperD HQ.md`
- `VERCEL.md`
- `MIGRATION-MANIFEST.md`

## Root exceptions

- `.git/`
- `.gitignore`
- `.env.local`
- `.claude/`, `.codex/`, `.codegraph/`, and `.cursor/`

Ignored dependency/build caches are excluded from the source migration. The following exact old paths were approved for cleanup before rebuilding dependencies:

- `.DS_Store`
- `07_Founder_Operating_System/.mypy_cache/`
- `07_Founder_Operating_System/.ruff_cache/`
- `07_Founder_Operating_System/.venv/`
- `07_Founder_Operating_System/__pycache__/`
- `obsidian/founder-intelligence/.next/`
- `obsidian/founder-intelligence/.vercel/`
- `obsidian/founder-intelligence/node_modules/`
- `obsidian/founder-intelligence/playwright-report/`
- `obsidian/founder-intelligence/test-results/`
- `obsidian/founder-intelligence/tsconfig.tsbuildinfo`
- `obsidian/research-agents/.mypy_cache/`
- `obsidian/research-agents/.pytest_cache/`
- `obsidian/research-agents/.ruff_cache/`
- `obsidian/research-agents/.venv/`
- `obsidian/website/.next/`
- `obsidian/website/.vercel/`
- `obsidian/website/node_modules/`
- `obsidian/website/playwright-report/`
- `obsidian/website/test-results/`
- `obsidian/website/tsconfig.tsbuildinfo`

The parent directories were removed after confirming they contained no files outside the approved cache/build classes. Dependencies are rebuilt under the new root-sibling project paths after cleanup.

## Safety gates

- Destination collision check passed before migration.
- Existing dirty work is user-owned and must remain intact.
- No compatibility symlinks are permitted.
- No credential values may enter this note, Git, logs, reports, or generated indexes.
