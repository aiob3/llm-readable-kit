# Comando /action — Orquestrador Memora Frontend

Você é o orquestrador do pipeline de design frontend para o sistema Memora.
Sua missão: garantir que ambas as skills estejam ativas e aplicá-las em sequência coordenada.

---

## FASE 0 — DIAGNÓSTICO OBRIGATÓRIO (sempre executar primeiro)

Antes de qualquer coisa, verificar se as skills estão instaladas:

```bash
# Verificar skill oficial da Anthropic
ls .claude/skills/frontend-design/SKILL.md 2>/dev/null && echo "OK:frontend-design" || echo "MISSING:frontend-design"

# Verificar skill Memora
ls .claude/skills/memora-frontend/SKILL.md 2>/dev/null && echo "OK:memora-frontend" || echo "MISSING:memora-frontend"
```

### Se `frontend-design` estiver MISSING → executar FASE 0A
### Se `memora-frontend` estiver MISSING → executar FASE 0B
### Se ambas OK → pular direto para FASE 1

---

## FASE 0A — AUTO-INSTALAÇÃO: frontend-design (Anthropic oficial)

```bash
mkdir -p .claude/skills/frontend-design

curl -fsSL \
  "https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md" \
  -o .claude/skills/frontend-design/SKILL.md

# Verificar se baixou corretamente
wc -l .claude/skills/frontend-design/SKILL.md
echo "✅ frontend-design instalado"
```

**Se curl falhar** (sem internet ou repositório privado):
1. Informar o usuário: "Não consegui baixar o frontend-design automaticamente."
2. Exibir instrução manual:
   ```
   Execute manualmente:
   mkdir -p .claude/skills/frontend-design
   curl -fsSL https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md \
     -o .claude/skills/frontend-design/SKILL.md
   ```
3. Continuar com apenas a skill memora-frontend, registrando o gap no relatório final.

---

## FASE 0B — AUTO-INSTALAÇÃO: memora-frontend (este plugin)

A skill memora-frontend está empacotada dentro deste próprio plugin.
Copiar da localização do plugin para o diretório de skills:

```bash
# Detectar localização do plugin (procurar plugin.json)
PLUGIN_DIR=$(find . -name "plugin.json" -path "*memora-frontend*" | head -1 | xargs dirname | xargs dirname)

mkdir -p .claude/skills/memora-frontend/references

cp "$PLUGIN_DIR/skills/memora-frontend/SKILL.md" \
   .claude/skills/memora-frontend/SKILL.md

cp "$PLUGIN_DIR/skills/memora-frontend/references/"* \
   .claude/skills/memora-frontend/references/ 2>/dev/null || true

echo "✅ memora-frontend instalado de $PLUGIN_DIR"
```

**Se não encontrar o plugin:** usar o agente `installer` para criar o SKILL.md inline.
Ver: `agents/installer.md`

---

## FASE 1 — LEITURA DAS SKILLS

Ler ambas as skills em sequência:

```
1. Ler .claude/skills/frontend-design/SKILL.md
   → Extrair: direção estética, regras de tipografia, filosofia "inesquecível"

2. Ler .claude/skills/memora-frontend/SKILL.md
   → Extrair: MDS tokens, contratos de API, componentes padrão, anti-patterns

3. Ler .claude/skills/memora-frontend/references/api-contract.md (se existir)
4. Ler .claude/skills/memora-frontend/references/postgres-schema.md (se existir)
```

---

## FASE 2 — BRIEFING DA TAREFA

Após carregar ambas as skills, fazer ao usuário (se não especificado no comando):

> "Qual componente/interface você quer criar agora?
> Exemplo: 'grafo de nodes', 'tabela de memórias', 'formulário CRUD', 'dashboard completo'"

Se o usuário já passou o argumento no comando (`/action grafo de nodes`), usar esse como briefing.
Pular a pergunta e ir direto para FASE 3.

---

## FASE 3 — PLANEJAMENTO DUAL-SKILL

Antes de escrever código, montar o plano combinando as duas skills:

### Do `frontend-design` (Anthropic):
- [ ] Qual direção estética? (escolher UMA: retro-futuristic / brutalist / refined dark / etc.)
- [ ] Qual tipografia com personalidade? (não usar Inter puro)
- [ ] O que torna este componente **inesquecível**?
- [ ] Qual animação/detalhe visual de alto impacto?

### Do `memora-frontend` (Memora):
- [ ] Qual API alimenta este componente? (`/api/graph` | `/api/memories` | `/api/views` | Postgres)
- [ ] Stack correto? (React+D3 | HTML single-file | React+shadcn)
- [ ] Tokens MDS aplicados? (`--mds-bg-base`, `--mds-accent-primary`, etc.)
- [ ] UX obrigatória do componente incluída? (zoom/pan, paginação, estados de erro)

**Apresentar o plano ao usuário antes de gerar código.**
Aguardar confirmação ou ajuste.

---

## FASE 4 — GERAÇÃO DO COMPONENTE

Com o plano aprovado, gerar o componente aplicando **ambas as skills simultaneamente**:

### Camada 1 — Memora (estrutura/dados):
Seguir os padrões de `memora-frontend`:
- Fetch das APIs corretas com tratamento de erro
- Design tokens `--mds-*` no `:root`
- Componentes com UX obrigatória

### Camada 2 — Anthropic frontend-design (estética):
Sobrepor os princípios da skill oficial:
- Tipografia com personalidade (Google Fonts ou system stack diferenciado)
- Direção estética clara e consistente
- Micro-animações e detalhes visuais que elevam o componente
- Evitar "AI slop" — nenhum card branco genérico

### Ordem de prioridade em caso de conflito:
```
memora-frontend > frontend-design
```
(o domínio específico do Memora prevalece sobre estética genérica)

---

## FASE 5 — RELATÓRIO FINAL

Ao terminar, exibir:

```markdown
## /action — Relatório de Execução

### Skills utilizadas:
- ✅ frontend-design (Anthropic oficial) — v[data do arquivo]
- ✅ memora-frontend — v1.0.0

### Direção estética escolhida: [nome]
### API conectada: [endpoint]
### Stack: [React/HTML/etc]

### Gaps identificados:
- [listar qualquer coisa que não foi possível aplicar e por quê]

### Próximo passo sugerido:
- [sugestão de componente complementar ou melhoria]
```

---

## Argumentos suportados

```
/action                          → modo interativo (pergunta o que criar)
/action grafo                    → gera o grafo de nodes/relations
/action tabela                   → gera a tabela de memórias
/action formulario               → gera o formulário CRUD
/action dashboard                → gera o painel completo (todos os componentes)
/action install                  → apenas instala as skills, não gera código
/action status                   → verifica status das skills sem gerar nada
```

---

## Comportamento em caso de falha parcial

| Cenário | Comportamento |
|---|---|
| `frontend-design` ausente + curl OK | Instala, continua normalmente |
| `frontend-design` ausente + sem internet | Continua com `memora-frontend` apenas, registra no relatório |
| `memora-frontend` ausente + plugin encontrado | Copia do plugin, continua |
| `memora-frontend` ausente + plugin não encontrado | Usa agente `installer` para recriar inline |
| Ambas ausentes | Instala as duas antes de prosseguir |
| Ambas presentes | Pula FASE 0, executa FASE 1 diretamente |
