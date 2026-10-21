#!/usr/bin/env bash
# Pratica 1 - PASSO 3: CARGA CONTROLADA (pequena, local, interrompivel).
# NAO e um DDoS. E um teste de carga legitimo contra o SEU servidor de teste.
# Detecta 'hey' (preferido) ou 'ab' (Apache Bench) automaticamente.
#
# Uso:   ./carga_controlada.sh <IP_SERVIDOR> [PORTA] [CAMINHO] [TOTAL] [CONCORRENCIA]
# Ex.:   ./carga_controlada.sh 192.168.56.10 8000 /relatorio 200 10
#
# LIMITES PADRAO (pequenos de proposito): 200 requisicoes, concorrencia 10.
# REGRAS:
#   - So contra o servidor de TESTE autorizado.
#   - Ctrl+C interrompe imediatamente.
#   - Se o host hospedeiro travar ou a memoria ficar critica, PARE JA.
set -euo pipefail

IP="${1:?Informe o IP do servidor. Ex.: ./carga_controlada.sh 192.168.56.10 8000 /relatorio 200 10}"
PORTA="${2:-8000}"
CAMINHO="${3:-/relatorio}"
TOTAL="${4:-200}"
CONC="${5:-10}"
URL="http://${IP}:${PORTA}${CAMINHO}"

# Trava de seguranca: impede valores grandes por engano.
if [ "${TOTAL}" -gt 2000 ] || [ "${CONC}" -gt 50 ]; then
  echo "ERRO: limites excedidos (TOTAL<=2000, CONC<=50). Esta aula usa carga PEQUENA." >&2
  exit 1
fi

echo "Alvo (servidor de teste autorizado): ${URL}"
echo "Total de requisicoes: ${TOTAL}   Concorrencia: ${CONC}"
echo "Ctrl+C para interromper a qualquer momento."
echo "==========================================================="

if command -v hey >/dev/null 2>&1; then
  echo "[usando hey]"
  hey -n "${TOTAL}" -c "${CONC}" "${URL}"
elif command -v ab >/dev/null 2>&1; then
  echo "[usando ab (Apache Bench)]"
  ab -n "${TOTAL}" -c "${CONC}" "${URL}"
else
  echo "Nem 'hey' nem 'ab' encontrados." >&2
  echo "Instale um deles:  Kali -> 'sudo apt install apache2-utils' (ab)" >&2
  echo "                   ou baixe 'hey'." >&2
  echo "Alternativa minima (sem relatorio): laco curl" >&2
  echo "  for i in \$(seq 1 ${TOTAL}); do curl -s -o /dev/null ${URL} & done; wait" >&2
  exit 1
fi

echo "==========================================================="
echo "Compare com a linha de base: subiu a latencia? apareceram falhas/5xx?"
echo "Rode monitorar_recursos.sh NO SERVIDOR durante este teste."
