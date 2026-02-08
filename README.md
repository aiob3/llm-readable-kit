# LLM Readable Kit

**Kit portável de extração de frameworks LLM-readable** para transformar conhecimento tácito de features de codebase em documentação estruturada e replicável.

Usa o protocolo **Fundation Agent** — um loop metacognitivo recursivo que gera artefatos padronizados (Feature Spec + Snippet Técnico + Guia de Adoção) a partir de qualquer feature de qualquer projeto.

---

## Quick Start

```bash
# 1. Copie a pasta docs-copy/ para o seu projeto
cp -r docs-copy/ /caminho/do/seu/projeto/docs-copy/

# 2. Preencha as variáveis em docs-copy/CODEX_TASK.md
#    FEATURE_NAME, CODEBASE_PATH, ENTRY_POINTS, TEST_FILE, TEST_COMMAND

# 3. Acione o agente com docs-copy/CODEX_TASK.md como entry point
```

## O que é

Este kit **não é um projeto de aplicação** — é um sistema de documentação/extração que:

1. **Recebe** a indicação de uma feature + acesso ao codebase
2. **Executa** um pipeline de 4 camadas (Ingestão → Enriquecimento → Projeção → Entrega)
3. **Produz** um `skill.md` contendo a tríade obrigatória:
   - **Feature Spec** — problema → solução → fluxo → critérios de aceite
   - **Snippet Técnico** — assinatura + pseudocódigo + código real + grafo de dependências
   - **Guia de Adoção** — pré-requisitos + passos + testes + troubleshooting
4. **Valida** via scoring logarítmico L0-L5 (mínimo 80/100)
5. **Aguarda** aprovação HITL (Human-in-the-Loop) — nunca auto-aprova

## Estrutura do Kit

```
docs-copy/                         ← ESTA PASTA é copiada para projetos-alvo
├── CODEX_TASK.md                  ← Entry point (ler PRIMEIRO)
├── fundation-agent.prompt.md      ← Protocolo do loop metacognitivo
├── feature-recurso-progressbar.md ← Referência estrutural (outro projeto)
├── framework-llm-readable.semantic-export.md ← Exemplo completo (READ-ONLY)
├── chunks/00..08-*.md             ← Instruções atômicas (carregar seletivamente)
├── components/                    ← Pasta de ENTREGA (output → revisão HITL)
│   ├── llm-readable.semantic-export.skill.md      ← Entregável aprovado
│   └── llm-readable.progress-bar-1-a-1.skill.md   ← Entregável aprovado
├── prompts/                       ← Prompts auxiliares
├── samples/                       ← Amostras de dados
└── reference_study_sop.md         ← Contexto histórico (opcional)
```

## Entregáveis Produzidos

| Feature | Arquivo | Status |
|---------|---------|--------|
| Semantic Export (Visual→LLM Bridge) | `components/llm-readable.semantic-export.skill.md` | Aprovado |
| Progress Bar 1-a-1 (FFmpeg) | `components/llm-readable.progress-bar-1-a-1.skill.md` | Aprovado |

## Para Agentes AI

Ler `.github/copilot-instructions.md` para convenções do projeto, ou ir direto para `docs-copy/CODEX_TASK.md` como entry point de execução.

## Autor

brito@vcia.com.br   |   linkedin.com/in/brito1   |    indygolab.com

## Licença

[MIT](LICENSE)
