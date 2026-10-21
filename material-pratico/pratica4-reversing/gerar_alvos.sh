#!/usr/bin/env bash
# Pratica 4 - PASSO 1: gerar os alvos a partir das fontes (rode no Kali).
# Produz em ./alvos: segredo.py, segredo.pyc, segredo.jar, segredo.exe, segredo.elf
# Todos sao BENIGNOS (codigo-fonte em ./fontes). Analise 100% estatica.
#
# Uso:   ./gerar_alvos.sh
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p alvos build
FALTOU=0

echo "================ Pratica 4 - geracao de alvos ================"

# --- 1) Interpretado: copia a fonte .py (nao ha compilacao) ---
cp fontes/segredo.py alvos/segredo.py
echo "[ok] alvos/segredo.py      (interpretado - fonte legivel)"

# --- 2) Bytecode Python (.pyc) ---
if command -v python3 >/dev/null 2>&1; then
  python3 -c "import py_compile; py_compile.compile('fontes/segredo.py', cfile='alvos/segredo.pyc')"
  echo "[ok] alvos/segredo.pyc     (bytecode Python)"
else
  echo "[FALTA] python3 - instale: sudo apt install python3"
  FALTOU=1
fi

# --- 3) .jar (bytecode Java) ---
if command -v javac >/dev/null 2>&1 && command -v jar >/dev/null 2>&1; then
  javac -d build fontes/Segredo.java
  ( cd build && jar cfe ../alvos/segredo.jar Segredo Segredo.class )
  echo "[ok] alvos/segredo.jar     (bytecode Java, executavel)"
else
  echo "[FALTA] JDK - instale: sudo apt install openjdk-17-jdk-headless"
  FALTOU=1
fi

# --- 4) .exe (PE Windows) via mingw-w64 ---
if command -v x86_64-w64-mingw32-gcc >/dev/null 2>&1; then
  x86_64-w64-mingw32-gcc -O0 fontes/segredo.c -o alvos/segredo.exe
  echo "[ok] alvos/segredo.exe     (PE Windows, codigo de maquina x86-64)"
else
  echo "[FALTA] mingw-w64 - instale: sudo apt install mingw-w64"
  FALTOU=1
fi

# --- 5) .elf (ELF Linux) via gcc ---
if command -v gcc >/dev/null 2>&1; then
  gcc -O0 fontes/segredo.c -o alvos/segredo.elf
  echo "[ok] alvos/segredo.elf     (ELF Linux, codigo de maquina x86-64)"
else
  echo "[FALTA] gcc - instale: sudo apt install build-essential"
  FALTOU=1
fi

echo "==============================================================="
if [ "${FALTOU}" -eq 1 ]; then
  echo "ATENCAO: faltou compilador(es). Rode o 'apt install' indicado"
  echo "acima e execute este script de novo. O que faltou NAO foi gerado."
else
  echo "Tudo gerado. Proximo passo: ./analisar_alvos.sh"
fi
