#!/usr/bin/env bash
# Pratica 3 - analise de captura (modo PRIMARIO, sempre funciona).
# Usa tshark para mostrar: (a) HTTP em texto claro (legivel) vs TLS (cifrado)
# no lab_trafego.pcap, e (b) o envenenamento ARP no arp_incident.pcap.
#
# Uso:   ./analisar_pcap.sh [DIR_DAS_CAPTURAS]
# Padrao: ../desafio-final  (onde o gerador salvou os .pcap)
set -uo pipefail
DIR="${1:-../desafio-final}"
LAB="${DIR}/lab_trafego.pcap"
ARP="${DIR}/arp_incident.pcap"

if ! command -v tshark >/dev/null 2>&1; then
  echo "tshark nao encontrado. Instale o Wireshark/tshark, ou abra os .pcap no Wireshark (modo grafico)." >&2
  exit 1
fi

echo "######################################################################"
echo "# PARTE 1: HTTP em TEXTO CLARO  vs  TLS CIFRADO  (${LAB})"
echo "######################################################################"
echo
echo ">> Requisicao HTTP (LEGIVEL - repare no caminho e nos cabecalhos):"
tshark -r "${LAB}" -Y 'http.request' -T fields -e ip.src -e http.request.method -e http.request.uri
echo
echo ">> Conteudo HTTP em texto (o que um interceptador LERIA):"
tshark -r "${LAB}" -Y 'http' -O http 2>/dev/null | grep -E 'GET|Host:|User-Agent:|X-Demo-Token:|status=' || true
echo
echo ">> Trafego TLS (porta 443) - repare: aparece como handshake CIFRADO,"
echo "   o conteudo NAO e legivel:"
tshark -r "${LAB}" -Y 'tls' -T fields -e ip.src -e ip.dst -e tls.record.content_type
echo "   (content_type 22 = handshake; nenhum texto da aplicacao aparece)"
echo
echo "######################################################################"
echo "# PARTE 2: ENVENENAMENTO DE CACHE ARP  (${ARP})"
echo "######################################################################"
echo
echo ">> Todos os pacotes ARP (opcode 1=pergunta, 2=resposta):"
tshark -r "${ARP}" -T fields -e frame.number -e arp.opcode \
       -e arp.src.hw_mac -e arp.src.proto_ipv4 -e arp.dst.proto_ipv4 \
       -E header=y -E separator='  '
echo
echo ">> SINAL SUSPEITO - um mesmo MAC reivindicando MAIS DE UM IP:"
tshark -r "${ARP}" -Y 'arp.opcode==2' -T fields -e arp.src.hw_mac -e arp.src.proto_ipv4 \
  | sort | uniq -c | sort -rn
echo
SUSPEITO="$(tshark -r "${ARP}" -Y 'arp.opcode==2' -T fields -e arp.src.hw_mac -e arp.src.proto_ipv4 \
  | sort -u | awk '{c[$1]++; ips[$1]=ips[$1]" "$2} END{for(m in c) if(c[m]>1) print m" ->"ips[m]}')"
if [ -n "${SUSPEITO}" ]; then
  echo "   MAC EM MAIS DE UM IP (classico de man-in-the-middle):"
  echo "${SUSPEITO}" | sed 's/^/     /'
else
  echo "   Nenhum MAC reivindicando mais de um IP nesta captura."
fi
echo
echo "DEFESAS: HTTPS com certificado validado, segmentacao/VLAN, inspecao"
echo "dinamica de ARP no switch, controle de acesso a rede."
