# Prática 4 — Engenharia reversa no Kali (roteiro do professor, passo a passo)

> **Regra absoluta:** análise **100% estática** — os alvos **nunca são executados** (nem o `.exe` na VM Windows). Tudo o que vamos descobrir sai das ferramentas: `file`, `strings`, `unzip`, `javap`, `objdump`. Os alvos são **benignos** (código-fonte aberto em `fontes/`), criados pelo próprio laboratório.
>
> **Tempo:** ~20–25 min · **Onde roda:** estação Kali (VM), sozinho ou em dupla.

## Ideia central da prática

Um arquivo "compilado" não é uma caixa-preta: ele carrega **strings, nomes, constantes e até código morto**. Quanto mais alto o nível do formato, mais legível — interpretado (`​.py`) mostra tudo; bytecode (`.pyc`, `.jar`) continua quase legível; código de máquina (`.exe`/`.elf`) exige uma camada a mais (`objdump`), mas **nada disso protege um segredo embutido** — só o dificulta.

## Passo 0 — gerar os alvos (Kali)

```bash
cd material-pratico/pratica4-reversing
./gerar_alvos.sh
```

*Esperado:* `[ok]` para `segredo.py`, `segredo.pyc`, `segredo.jar`, `segredo.exe`, `segredo.elf`. Se faltar compilador, o script diz o `apt install` — rode-o e repita. *(Plano B: o professor pode levar os alvos já gerados no pendrive.)*

## Passo 1 — reconhecer os formatos

```bash
file alvos/*
```

*Esperado:*
```
alvos/segredo.elf:  ELF 64-bit LSB pie executable, x86-64
alvos/segredo.exe:  PE32+ executable (console) x86-64, for MS Windows
alvos/segredo.jar:  Java archive data (JAR)
alvos/segredo.pyc:  python 3.x byte-compiled
alvos/segredo.py:   Python script, ASCII text executable
```
Discuta: quais são **interpretados**, quais são **bytecode** e quais são **código de máquina**?

## Passo 2 — a fonte interpretada (nada esconde)

```bash
cat alvos/segredo.py
```

*Esperado:* a flag `FLAG{py_codigo_aberto}` e a "senha" aparecem **na primeira leitura**. Interpretado não compila nada — distribuir `.py` é distribuir a lógica inteira.

## Passo 3 — o bytecode Python (.pyc)

```bash
strings -a -n 4 alvos/segredo.pyc
```

*Esperado:* `FLAG{py_codigo_aberto}`, `segredo_interno`, `SENHA_FICTICIA` — **visíveis como texto**. Compilar para `.pyc` não esconde strings nem nomes. *(Opcional: `sudo apt install pycdc && pycdc alvos/segredo.pyc` devolve quase a fonte original.)*

## Passo 4 — o bytecode Java (.jar)

```bash
unzip -l alvos/segredo.jar
javap -c -p -cp alvos/segredo.jar Segredo
```

*Esperado:* o `.jar` é um **ZIP** (`unzip -l` lista `Segredo.class`); o `javap` desmonta o bytecode e mostra as constantes `FLAG{jar_javap_legivel}` e `senha-lab-123` praticamente como na fonte — inclusive o método `segredoInterno()`, que **nunca é chamado** mas foi parar inteiro no arquivo.

## Passo 5 — o código de máquina (.exe / .elf)

```bash
strings -a -n 4 alvos/segredo.exe | grep -Ei 'flag|senha|benigno'
```

*Esperado:* `FLAG{exe_strings_facil}`, `FLAG{exe_dead_code}`, `SenhaForte123`, `Programa benigno do lab...` — o binário carrega tudo isso em claro. Mas a terceira flag **não aparece**: ela está ofuscada.

```bash
objdump -h alvos/segredo.exe | grep -E 'Idx|.rdata|.data'
objdump -s -j .rdata alvos/segredo.exe
```

*Esperado:* nas constantes aparece um bloco de bytes "sem sentido" (o XOR). Agora decodifique (copie os bytes hex do array `SEGREDO_XOR` que aparecem no dump, sem espaços):

```bash
python3 -c "print(bytes(b ^ 0x42 for b in bytes.fromhex('040e0305 39273a271d3a2d30 1d76703f'.replace(' ',''))).decode())"
```

*Esperado:* `FLAG{exe_xor_42}` — a decodificação revela a flag ofuscada.

```bash
file alvos/segredo.elf
strings -a -n 4 alvos/segredo.elf | grep -Ei 'flag|senha'
```

*Esperado:* o `.elf` contém **as mesmas** flags do `.exe` — PE (Windows) e ELF (Linux) são apenas "embalagens" diferentes para o mesmo conceito de código de máquina.

## Passo 6 — concluir com a turma (5 min)

1. **Nenhum formato protegeu o segredo.** A diferença foi só o *esforço*: `.py` (zero), `.pyc`/`.jar` (quase zero), `.exe` (uma camada a mais).
2. **Código morto viaja junto:** funções nunca chamadas permanecem no binário — e podem carregar credenciais.
3. **Ofuscação (XOR) só atrasa:** qualquer constante embutida pode ser revertida com o binário em mãos. Segredo de verdade não se embute em código — vai para cofre/gerenciador de segredos.
4. **Conexão com incidentes reais:** vazamentos de credenciais hardcoded em apps e firmware de IoT seguem exatamente esse caminho (strings → segredo).

## Plano alternativo (se faltar compilador no Kali)

- Sem `mingw-w64`/`javac`: analise apenas `.py` + `.pyc` (Passos 2–3) e use os alvos `.exe`/`.jar` **pré-gerados pelo professor** (pendrive) nos Passos 4–5.
- Sem nada disso: o Passo 2 (`.py`) + a comparação conceitual já sustentam a discussão do Passo 6.

## Segurança e encerramento

- **Nunca execute** `segredo.exe`/`segredo.elf`/`segredo.jar` — a prática é estática; a mensagem "benigno" é apenas isso, uma mensagem.
- Os alvos são gerados a partir de `fontes/` locais e podem ser apagados ao final (`rm -rf alvos build`), ou arquivados como evidência da aula.
- Evidência para a folha de registro: uma captura de tela por flag extraída + a ferramenta usada.
