#!/usr/bin/env bash
# Pratica 4 - PASSO 2: analise ESTATICA dos alvos (NUNCA executa o alvo!).
# Mostra o que cada formato revela: file, sha256, strings, javap, objdump.
#
# Uso:   ./analisar_alvos.sh [arquivo ...]     (padrao: todos os alvos gerados)
set -uo pipefail
cd "$(dirname "$0")"

if [ "$#" -eq 0 ]; then
  set -- alvos/segredo.py alvos/segredo.pyc alvos/segredo.jar alvos/segredo.exe alvos/segredo.elf
fi

for ALVO in "$@"; do
  echo "======================================================================"
  echo " ALVO: ${ALVO}"
  echo "======================================================================"
  if [ ! -f "${ALVO}" ]; then
    echo "  [arquivo nao encontrado - rode ./gerar_alvos.sh primeiro]"
    echo
    continue
  fi

  echo "-- file (que formato e este?) --"
  file "${ALVO}"
  echo "-- sha256 (integridade/identificacao) --"
  sha256sum "${ALVO}"
  echo

  case "${ALVO}" in
    *.py)
      echo "-- INTERPRETADO: a 'compilacao' nao existe - o codigo E o arquivo --"
      sed -n '1,20p' "${ALVO}"
      ;;

    *.pyc)
      echo "-- BYTECODE Python: strings continuam legiveis --"
      strings -a -n 4 "${ALVO}" | grep -Ei 'FLAG|senha|segredo' || true
      echo
      echo " (dica: decompilador completo -> 'sudo apt install pycdc' e pycdc ${ALVO})"
      ;;

    *.jar)
      echo "-- BYTECODE Java: o .jar e um ZIP - liste e extraia --"
      unzip -l "${ALVO}"
      TMPD="$(mktemp -d)"
      unzip -q -o "${ALVO}" -d "${TMPD}"
      echo "-- javap -c -p: desmonta o bytecode (constantes ficam visiveis) --"
      javap -c -p -classpath "${TMPD}" Segredo 2>/dev/null | grep -E 'String |ldc' | head -15
      rm -rf "${TMPD}"
      ;;

    *.exe|*.elf)
      echo "-- CODIGO DE MAQUINA: strings visiveis --"
      strings -a -n 4 "${ALVO}" | grep -Ei 'FLAG|senha|benigno' || true
      echo
      echo "-- secoes do binario (.rdata/.rodata guardam constantes; .data, o XOR) --"
      objdump -h "${ALVO}" | awk 'NR<=6 || /\.(rdata|rodata|data)/'
      echo
      echo "-- dump das secoes de dados (procure bytes 'estranhos' = ofuscados) --"
      for SEC in .rdata .rodata .data; do
        objdump -s -j "${SEC}" "${ALVO}" 2>/dev/null | head -12 && break
      done
      echo
      echo " (dica: bytes XOR 0x42 -> decodifique com python3 -c \"import sys;print(bytes(b^0x42 for b in bytes.fromhex('COLE_AQUI')).decode())\")"
      ;;

    *)
      echo "-- formato nao mapeado; rode: file ${ALVO} ; strings -a ${ALVO} --"
      ;;
  esac
  echo
done

echo "======================================================================"
echo " RECAPITULACAO (o que cada formato esconde - ou nao):"
echo "  .py  = fonte aberta .......... nada esconde"
echo "  .pyc = bytecode Python ....... strings e nomes continuam legiveis"
echo "  .jar = bytecode Java ......... idem (javap le quase como a fonte)"
echo "  .exe/.elf = codigo de maquina  strings passam; dados ofuscados exigem objdump + decodificacao"
echo " NENHUM formato protege segredos embutidos - so os dificulta."
