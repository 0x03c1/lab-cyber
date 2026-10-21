#!/usr/bin/env bash
# Pratica 1 - monitoramento de recursos do SERVIDOR durante a carga.
# Rode ESTE script NO HOST QUE EXECUTA o servidor_teste.py, em outra aba.
# Mostra, a cada 2s, o uso de CPU/memoria do processo python do servidor e
# o numero de conexoes na porta. Ctrl+C para parar.
#
# Uso:   ./monitorar_recursos.sh [PORTA]
# Ex.:   ./monitorar_recursos.sh 8000
set -uo pipefail
PORTA="${1:-8000}"

echo "Monitorando processo do servidor (porta ${PORTA}). Ctrl+C para parar."
echo "timestamp            | %CPU  %MEM  | conexoes_na_porta"
echo "---------------------------------------------------------------"
while true; do
  TS="$(date '+%Y-%m-%d %H:%M:%S')"

  # CPU/MEM do(s) processo(s) python do servidor de teste
  LINHA="$(ps -A -o pcpu,pmem,command 2>/dev/null | grep -i "servidor_teste.py" | grep -v grep | head -1)"
  if [ -n "${LINHA}" ]; then
    CPU="$(echo "${LINHA}" | awk '{print $1}')"
    MEM="$(echo "${LINHA}" | awk '{print $2}')"
  else
    CPU="--"; MEM="--"
  fi

  # Conexoes na porta (Linux: ss; macOS: lsof)
  if command -v ss >/dev/null 2>&1; then
    CONN="$(ss -tn state established "( sport = :${PORTA} )" 2>/dev/null | grep -c ':')"
  elif command -v lsof >/dev/null 2>&1; then
    CONN="$(lsof -nP -iTCP:"${PORTA}" -sTCP:ESTABLISHED 2>/dev/null | grep -c ':')"
  else
    CONN="--"
  fi

  printf "%s | %4s  %4s  | %s\n" "${TS}" "${CPU}" "${MEM}" "${CONN}"
  sleep 2
done
