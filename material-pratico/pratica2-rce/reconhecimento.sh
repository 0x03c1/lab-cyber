#!/usr/bin/env bash
# Pratica 2 - PASSO 2: reconhecimento de servicos do ALVO DE LABORATORIO.
# Executa 'nmap -sV' e explica como ler a saida. SOMENTE contra o alvo
# deliberadamente vulneravel, isolado e autorizado (Metasploitable).
#
# Uso:   ./reconhecimento.sh <IP_ALVO>
# Ex.:   ./reconhecimento.sh 192.168.56.40
set -euo pipefail
IP="${1:?Informe o IP do alvo de laboratorio. Ex.: ./reconhecimento.sh 192.168.56.40}"

cat <<'TXT'
======================================================================
 RECONHECIMENTO DE SERVICOS (nmap -sV)
 Regra: so contra alvo de laboratorio isolado e AUTORIZADO.
======================================================================
TXT

if ! command -v nmap >/dev/null 2>&1; then
  echo "nmap nao encontrado. No Kali ja vem instalado; senao: sudo apt install nmap" >&2
  echo "PLANO B: use recon_services.txt (saida ja preparada) para a analise." >&2
  exit 1
fi

echo "Confirme antes de prosseguir:"
echo "  - ${IP} e um ALVO DE LABORATORIO isolado? (deveria ser)"
echo "  - voce esta AUTORIZADO a escanear? (deveria estar)"
echo
echo "Executando: nmap -sV ${IP}"
echo "----------------------------------------------------------------------"
# -sV detecta versao dos servicos. Sem flags agressivas.
nmap -sV "${IP}"
echo "----------------------------------------------------------------------"
cat <<'TXT'
COMO LER:
  - Cada linha PORT/STATE/SERVICE/VERSION mostra um servico exposto e sua versao.
  - "Superficie de ataque" = tudo que esta 'open' sem necessidade.
  - Versoes ANTIGAS costumam ter vulnerabilidades conhecidas (consulte CVE/NVD).
  - Anote o servico/versao que sera o foco (sugestao de lab: FTP vsftpd 2.3.4).
PROXIMO PASSO: roteiro-metasploit.md (inspecionar o modulo e seus requisitos).
TXT
