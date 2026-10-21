#!/usr/bin/env bash
# Pratica 1 - PASSO 2: medir a LINHA DE BASE (antes da carga).
# Faz N medicoes simples com curl e mostra tempo de resposta e codigo HTTP.
# Execute na ESTACAO CLIENTE (Kali/Windows-com-curl), apontando para o servidor.
#
# Uso:   ./medir_baseline.sh <IP_SERVIDOR> [PORTA] [CAMINHO]
# Ex.:   ./medir_baseline.sh 192.168.56.10 8000 /status
set -euo pipefail

IP="${1:?Informe o IP do servidor. Ex.: ./medir_baseline.sh 192.168.56.10 8000 /status}"
PORTA="${2:-8000}"
CAMINHO="${3:-/status}"
URL="http://${IP}:${PORTA}${CAMINHO}"

echo "Medindo linha de base em: ${URL}"
echo "(10 requisicoes sequenciais)"
echo "-------------------------------------------"
for i in $(seq 1 10); do
  curl -o /dev/null -s -w "req %{http_code}  tempo_total=%{time_total}s\n" "${URL}" || echo "req FALHOU (servidor no ar?)"
done
echo "-------------------------------------------"
echo "ANOTE o tempo tipico e o codigo (esperado: 200 e tempo baixo)."
echo "Repita este script DURANTE a carga para comparar."
