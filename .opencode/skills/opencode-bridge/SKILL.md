---
name: opencode-bridge
description: Integração com OpenCode CLI. Use para explorar codebases, automação com glob/grep, ou quando OpenCode tiver ferramentas únicas não disponíveis em outras CLIs.
---

# OpenCode Bridge

## Ferramentas Disponíveis

| Ferramenta | Uso | Melhor Para |
|------------|-----|-------------|
| `glob` | Encontrar arquivos por padrão | Exploração rápida |
| `grep` | Buscar conteúdo em arquivos | Encontrar código |
| `read` | Ler arquivos | Análise precisa |
| `write` | Criar arquivos | Novos arquivos |
| `edit` | Editar arquivos | Modificações precisas |
| `bash` | Executar comandos shell | Automação |
| `websearch` | Pesquisa web em tempo real | Informação atualizada |
| `codesearch` | Busca código via Exa Code API | Documentação API |
| `task` | Agentes especializados | Tarefas complexas |
| `todowrite` | Rastreamento de tarefas | Planejamento |
| `question` | Interação com usuário | Decisões |

## Quando Usar OpenCode

| Cenário | Por que OpenCode |
|---------|-----------------|
| Exploração de codebase | glob + grep mais rápido que alternativas |
| Edição precisa de arquivos | read + edit com contexto exato |
| Automação Windows | Integração shell nativa |
| Rastreamento de tarefas | todowrite para planning |
| Pesquisa web | websearch em tempo real |
| Busca de código | codesearch via Exa API |

## Comparação com Outras CLIs

| Recurso | Codex | Claude Code | OpenCode |
|---------|-------|-------------|----------|
| Exploração | grep | grep | **glob + grep** |
| Editar | diff | edit | **read + edit** |
| Tarefas | skill | /feature-dev | **todowrite** |
| Web | — | websearch | **websearch** |
| Agentes | task | agents | **task** |

## Invocação

```bash
# Via Codex, pode invocar OpenCode:
opencode --help
opencode "explore this codebase"

# Via Claude Code:
opencode -p "task"
```

## Integração com cross-cli-bridge

Esta skill complementa `cross-cli-bridge` fornecendo detalhes específicos do OpenCode para roteamento de tarefas.
