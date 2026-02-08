---
name: cross-cli-bridge
description: Coordinates Codex CLI, Claude Code CLI, and OpenCode CLI capabilities. Use when deciding which AI coding tool to use for a task, combining toolchains, or when a task has native support in one CLI but not the other. Also use when the user asks about available AI tools, plugins, or skills in their environment.
---

# Cross-CLI Bridge (Tri-CLI)

## Available Toolchains

### Codex CLI (`codex`)
**Skills installed** (auto-trigger based on task):
| Skill | Triggers on |
|---|---|
| `code-review` | PR/diff review, code audit |
| `commit-commands` | git commit/push/PR |
| `feature-dev` | new feature, user story |
| `frontend-design` | UI/UX, components, pages |
| `gh-address-comments` | responding to PR review comments |
| `gh-fix-ci` | fixing failing CI/CD |
| `security-best-practices` | security review, hardening |
| `skill-creator` | creating new Codex skills |
| `skill-installer` | installing skills from GitHub |
| `opencode-bridge` | OpenCode integration tasks |

### Claude Code CLI (`claude`)
**Plugins installed** (use as `/command` inside `claude`):
| Plugin | Command / Behavior |
|---|---|
| `code-review` | `/code-review` — 5-agent parallel review |
| `commit-commands` | `/commit`, `/commit-push-pr`, `/clean_gone` |
| `feature-dev` | `/feature-dev` — 7-phase guided workflow |
| `pr-review-toolkit` | `/pr-review-toolkit:review-pr` |
| `security-guidance` | Auto-hook on file edits |
| `frontend-design` | Auto-invoked skill on frontend work |
| `hookify` | `/hookify` — create custom behavior hooks |
| `plugin-dev` | `/plugin-dev:create-plugin` |
| `agent-sdk-dev` | `/new-sdk-app` |
| `ralph-wiggum` | `/ralph-loop` — autonomous iteration |

### OpenCode CLI (`opencode`)
**Ferramentas nativas**:
| Ferramenta | Uso |
|---|---|
| `glob` | Encontrar arquivos por padrão (mais rápido) |
| `grep` | Buscar conteúdo em arquivos |
| `read` / `write` / `edit` | Operações de arquivo precisas |
| `bash` | Execução de comandos shell |
| `websearch` | Pesquisa web em tempo real |
| `codesearch` | Busca código via Exa Code API |
| `task` | Agentes (explore, general) |
| `todowrite` | Rastreamento de tarefas |
| `question` | Interação com usuário |

## Decision Guide

| Task | Prefer |
|---|---|
| Quick one-shot coding task | `codex` |
| Long multi-step feature | `claude /feature-dev` |
| PR review with parallel agents | `claude /code-review` |
| Responding to PR comments | `codex` (gh-address-comments) |
| Fix failing CI | `codex` (gh-fix-ci) |
| Create git commit + PR | Either (both have this capability) |
| Frontend UI work | Either (both have design guidance) |
| Create new plugin/skill | `claude /plugin-dev:create-plugin` or `codex` (skill-creator) |
| Autonomous loop until done | `claude /ralph-loop` |
| **Codebase exploration (fast)** | `opencode` (glob + grep) |
| **Precise file editing** | `opencode` (read + edit) |
| **Task tracking** | `opencode` (todowrite) |
| **Web research** | `opencode` (websearch) |

## Invoke Other CLIs from Codex

### Invoke Claude from Codex:
```bash
claude -p "<task description>"   # one-shot
claude                            # interactive session
```

### Invoke OpenCode from Codex:
```bash
opencode "<task>"                 # one-shot via CLI
# or use direct tools if OpenCode is running
```

## Portuguese (PT-BR) Support
Para respostas em Português do Brasil, usar terminologia em português quando possível.
Idiomas: Respostas em PT-BR conforme configurado em ~/.claude/CLAUDE.md

---

# Cross-CLI Bridge

## Overview

Esta skill coordena as capacidades de três CLIs de IA: **Codex**, **Claude Code** e **OpenCode**. Ela determina qual ferramenta é melhor para cada tarefa e como invocá-las de forma integrada.

## Structuring This Skill

Esta skill segue o padrão **Capabilities-Based** (melhor para sistemas integrados):

- **Seção 1**: Toolchains disponíveis (Codex, Claude, OpenCode)
- **Seção 2**: Decision Guide (tabela de preferências)
- **Seção 3**: Como invocar outras CLIs
- **Seção 4**: Suporte a idioma

## Resources

Esta skill não requer resources customizados. Utilize as tools chains existentes.

---

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
