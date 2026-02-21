# Entregável de Avaliação do Memora

Data: 2026-02-20
Escopo: consolidar registros de evolução e disponibilizar critérios objetivos para o Operador avaliar o uso do Memora a partir deste ponto.

## 1) Registros gravados no Memora

Memórias criadas nesta iteração:
- `#2` HITL e governança (autoridade do Operador, consulta obrigatória em dúvidas)
- `#3` Hardening de configuração e baseline de ambiente
- `#4` Padronização do runtime (`memora` padrão, `memory-keeper` descontinuado, rollback controlado)
- `#5` Operação do Graph (modo persistente `sse`, scripts corrigidos)
- `#6` Checklist de avaliação do Operador (status aberto, prioridade alta)
- `#7` Registro do próprio entregável para rastreabilidade operacional

Correção de integridade aplicada:
- `#1` teve normalização de formato de tags para JSON válido.

Resumo de estado após registro:
- Total de memórias: `7`
- Total de ações: `7`

## 2) Features disponibilizadas para operação

- Runtime oficial Memora instalado no workspace (`.opencode/.venv-memora`).
- Padrão de memória consolidado em Memora.
- Graph local operacional em `http://127.0.0.1:8765/graph`.
- Endpoint MCP SSE operacional em `http://127.0.0.1:8000/sse`.
- Scripts de start atualizados com healthcheck/retry:
  - `.opencode/start-memora-graph.sh`
  - `.opencode/start-memora-graph.ps1`
  - `.opencode/start-memora-graph.bat`

## 3) Evidências para validação do Operador

### Subida do Graph
```bash
bash .opencode/start-memora-graph.sh
curl -i http://127.0.0.1:8765/graph
```

### Inspeção de dados do grafo
```bash
curl -i http://127.0.0.1:8765/api/graph
```

### Verificação de memória e ações (SQLite)
```bash
python3 - <<'PY'
import sqlite3
conn=sqlite3.connect('.opencode/memory/memoria.db')
cur=conn.cursor()
cur.execute('select count(*) from memories')
print('memories_total', cur.fetchone()[0])
cur.execute('select count(*) from memories_actions')
print('actions_total', cur.fetchone()[0])
cur.execute('select id, action, summary, timestamp from memories_actions order by id desc limit 10')
for r in cur.fetchall():
    print(r)
conn.close()
PY
```

## 4) Avaliação HITL (esforço, impacto, pareto)

### Opção A: Operação mínima (manter como está)
- Esforço: baixo
- Impacto: médio
- Pareto: cobre ~80% do valor com ~20% do esforço
- Quando usar: foco em continuidade sem automação adicional

### Opção B: Operação controlada com rotina semanal
- Esforço: médio
- Impacto: alto
- Pareto: melhor equilíbrio para governança contínua
- Quando usar: necessidade de rastreabilidade estável (memórias + ações + graph)

### Opção C: Operação avançada (automações + auditoria contínua)
- Esforço: alto
- Impacto: alto
- Pareto: retorno adicional menor no curto prazo
- Quando usar: exigência de compliance rígido e histórico aprofundado

## 5) Critério de aceite do operador

- Graph acessível com HTTP 200 em `/graph`.
- `/api/graph` retornando payload válido.
- Memórias `#2..#7` visíveis na base.
- Trilha de ações contendo operações `create` nesta iteração.
- Política HITL presente e rastreável no registro de memória.
