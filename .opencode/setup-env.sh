#!/usr/bin/env bash
# Carrega variáveis de ambiente locais para MCPs sem versionar segredos.

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ROOT_DIR="$(cd "${BASE_DIR}/.." >/dev/null 2>&1 && pwd)"
ROOT_ENV_FILE="${ROOT_DIR}/.env"
LOCAL_ENV_FILE="${BASE_DIR}/.env"
ENV_EXAMPLE_FILE="${BASE_DIR}/.env.example"

load_env_file() {
    local file="$1"
    while IFS= read -r line || [ -n "$line" ]; do
        # Ignora linhas vazias e comentários
        [[ -z "${line// }" || "${line#\#}" != "$line" ]] && continue

        # Exporta apenas linhas no formato KEY=VALUE
        if [[ "$line" == *=* ]]; then
            local key="${line%%=*}"
            local value="${line#*=}"
            export "$key=$value"
        fi
    done < "$file"
}

if [ -f "$ROOT_ENV_FILE" ]; then
    echo "Carregando variaveis de ambiente de ${ROOT_ENV_FILE}"
    load_env_file "$ROOT_ENV_FILE"
    echo "Variaveis carregadas com sucesso."
elif [ -f "$LOCAL_ENV_FILE" ]; then
    echo "Carregando variaveis de ambiente de ${LOCAL_ENV_FILE}"
    load_env_file "$LOCAL_ENV_FILE"
    echo "Variaveis carregadas com sucesso."
else
    echo "Arquivo .env nao encontrado na raiz (${ROOT_ENV_FILE}) nem em .opencode (${LOCAL_ENV_FILE})."
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        echo "Use ${ENV_EXAMPLE_FILE} como base para criar o .env."
    fi
fi

echo "Ambiente Tri-CLI preparado."
