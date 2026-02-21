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

## Protocolo Memora (Obrigatório)

Toda conversa nova deve iniciar com registro de sessão no Memora e seguir com checkpoints, inferências, decisões e entregas.

- Arquivo de referência: `.agentic/MEMORA-PERSISTENT-PROTOCOL.md`
- Ferramenta de registro: `.agentic/scripts/memora_ops.py`

Fluxo mínimo:
1. `start` no primeiro prompt da conversa
2. `checkpoint` e `change` durante a execução
3. `inference`/`decision` quando houver dúvida ou trade-off
4. `delivery` e `end` no fechamento
