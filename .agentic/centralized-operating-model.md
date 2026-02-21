# Modelo Operacional Centralizado Multiagente

## Objetivo Final
Consolidar um cenario unico de operacao para interfaces agenticas CLI com quatro frentes:
1. Copilot
2. Codex
3. Claude
4. OpenCode

O foco e manter uma base unica para skills, MCPs e features habilitadas, com seguranca e replicabilidade.

## Estado Atual Consolidado
- Branches convergidas no GitHub: `master` e `chunkit` no mesmo commit.
- Topologia MCP centralizada em `opencode.json`.
- Features OpenCode centralizadas em `.opencode/config.json`.
- Plugins Claude centralizados em `.claude/settings.json`.
- Regra operacional do kit centralizada em `.github/copilot-instructions.md`.
- Registro unificado criado em `.agentic/registry.yaml`.
- Memoria padrao consolidada em `memora`; `memory-keeper` retirado da configuracao ativa.

## Estrutura de Centralizacao

### Camada 1: Governanca (SSOT)
- `.agentic/registry.yaml`: inventario oficial (interfaces + MCPs + politicas).
- `.agentic/centralized-operating-model.md`: estrategia e roadmap de execucao.
- `.agentic/MEMORA-PERSISTENT-PROTOCOL.md`: protocolo mandatorio de memoria persistente.
- `.agentic/scripts/memora_ops.py`: logger atomico/idempotente para trilha operacional.

### Camada 2: Runtime Seguro
- `opencode.json`: sem segredos versionados e com MCPs externos desabilitados por padrao.
- `.opencode/.env.example`: template de variaveis obrigatorias.
- `.opencode/setup-env.sh`: bootstrap local de ambiente.
- `.gitignore`: bloqueio de arquivos sensiveis locais.

### Camada 3: Padronizacao de Repositorio
- `.gitattributes`: normalizacao de EOL para eliminar ruido de CRLF/LF entre CLIs.

## Matriz de Papel por Interface
| Interface | Papel Primario | Fonte de Configuracao |
|---|---|---|
| Copilot | Framework docs-copy / Fundation Agent | `.github/copilot-instructions.md` |
| Codex | Execucao tecnica e automacao de consolidacao | `AGENTS.md` + workspace |
| Claude | Workflows longos, review e commit assistido | `.claude/CLAUDE.md`, `.claude/settings.json` |
| OpenCode | Exploracao rapida e orquestracao local | `.opencode/config.json`, `.opencode/skills/*` |

## Roadmap de Consolidacao (Centralizado)

### Fase 1 (concluida neste ciclo)
1. Remocao de segredos versionados do `opencode.json`.
2. Criação de baseline de segredos em `.opencode/.env.example`.
3. Padronizacao de linha com `.gitattributes`.
4. Registro central inicial em `.agentic/registry.yaml`.

### Fase 2 (proximo ciclo)
1. Criar `opencode.local.json` (nao versionado) para overrides por maquina.
2. Definir check de CI para falhar em deteccao de segredo em JSON/YAML.
3. Publicar checklist unico para onboarding de interface CLI.

### Fase 3 (operacao continua)
1. Revisao semanal de inventario MCP/skills/plugins.
2. Revisao mensal de superfice de segredo (rotacao de chaves).
3. Revisao trimestral de redundancias entre interfaces.

## Procedimento de Replicacao para Novo Workspace
1. Clonar repositorio e copiar `.opencode/.env.example` para `.env` na raiz.
2. Preencher variaveis locais e executar `.opencode/setup-env.sh`.
3. Habilitar MCPs externos no `opencode.json` apenas apos segredo validado.
4. Validar consistencia com `.agentic/registry.yaml`.
5. Iniciar trabalho usando a matriz de papel por interface deste documento.

## Criterio de Sucesso
O workspace e considerado centralizado quando:
1. Nenhum segredo existe em arquivo versionado.
2. Inventario `.agentic/registry.yaml` esta atualizado.
3. EOL nao gera diffs ruidosos entre interfaces.
4. Skills, MCPs e features possuem fonte de verdade unica e auditavel.

## Regra HITL (Autoridade do Operador)
1. O Operador e a autoridade final de decisao.
2. Em caso de duvida, o assistente deve consultar o Operador antes de decidir.
3. O assistente deve apresentar alternativas com analise de esforco, impacto e recorte pareto para facilitar a decisao.

## Evolucao Metacognitiva Assistida por Memora
1. Toda sessao inicia com registro `start` no primeiro prompt.
2. Toda hipotese/incerteza relevante gera registro `inference`.
3. Toda decisao de trade-off gera registro `decision` com alternativas e pareto.
4. Todo marco de implementacao gera `checkpoint`/`change`.
5. Todo encerramento gera `delivery` e `end`.
6. Reexecucao do mesmo evento e idempotente por `event_key` deterministico.
