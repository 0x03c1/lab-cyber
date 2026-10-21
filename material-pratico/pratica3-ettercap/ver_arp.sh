#!/usr/bin/env bash
# Pratica 3 - mostrar a tabela ARP atual e destacar MAC duplicado.
# Funciona em Linux (ip neigh / arp) e macOS (arp). No Windows: use 'arp -a'.
# Uso:   ./ver_arp.sh
set -uo pipefail

echo "=============================================="
echo " Tabela ARP atual desta maquina"
echo "=============================================="
if command -v ip >/dev/null 2>&1; then
  ip neigh
  echo "----------------------------------------------"
  echo "MACs que aparecem para MAIS DE UM IP (suspeito):"
  ip neigh | awk '$5 != "ff:ff:ff:ff:ff:ff"' | awk '/lladdr/ {print $5, $1}' | sort -u | awk '{c[$1]=c[$1]" "$2} END{for(m in c){n=split(c[m],a," "); if(n>1) print "  MAC", m, "->", c[m]}}'
elif command -v arp >/dev/null 2>&1; then
  arp -a
  echo "----------------------------------------------"
  echo "MACs que aparecem para MAIS DE UM IP (suspeito):"
  arp -a | awk '$4 != "(incomplete)" && $4 != "ff:ff:ff:ff:ff:ff" {print $4, $2}' | sort -u | awk '{c[$1]=c[$1]" "$2} END{for(m in c){n=split(c[m],a," "); if(n>1) print "  MAC", m, "->", c[m]}}'
else
  echo "Nem 'ip' nem 'arp' disponiveis. No Windows use: arp -a"
fi
echo
echo "No WINDOWS, rode no Prompt/PowerShell:  arp -a"
echo "Procure: dois IPs com o MESMO endereco fisico (MAC) = sinal de MITM."
