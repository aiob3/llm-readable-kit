# Instruções do Projeto

## Contexto
Este projeto usa a convergência Tri-CLI (Codex + Claude Code + OpenCode).

## Ferramentas Disponíveis

| Tarefa | CLI Preferida |
|--------|---------------|
| Exploração de código | `opencode` (glob + grep) |
| Code Review | `codex code-review` ou `claude /code-review` |
| Nova feature | `claude /feature-dev` |
| Commit + PR | `claude /commit` |
| Automação | `opencode bash` |

## Comandos Úteis

```bash
# Verificar skills disponíveis
codex --list-skills

# Ver plugins Claude
claude plugin list
```
