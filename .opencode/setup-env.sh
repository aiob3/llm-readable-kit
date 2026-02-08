#!/bin/bash
# ==============================================================================
# Script de Inicialização de Ambiente Tri-CLI Seguro
# Carrega as variáveis de ambiente necessárias para os MCPs do Copilot
# (Firecrawl, Exa, Browserbase, Memory-Keeper) sem expô-las no código.
# ==============================================================================

# Diretório base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ENV_FILE="$BASE_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo "🔑 Carregando segredos e configurações do arquivo .env..."
    # Carrega as variáveis de ambiente ignorando linhas em branco ou comentários
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo "✅ Variáveis de ambiente configuradas com sucesso."
else
    echo "⚠️  Aviso: Arquivo .env não encontrado em $ENV_FILE"
    echo "    Certifique-se de configurar as API Keys para Firecrawl, Exa e Browserbase."
fi

echo "🚀 O ambiente Tri-CLI está pronto para uso!"
echo "    Você pode executar comandos 'claude' ou 'codex' com suporte total aos MCPs."
