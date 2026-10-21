# Atividade — "Caça às bandeiras: o que o binário esconde?" (material dos alunos)

> Vocês são a equipe de análise da **Sertão Digital**. A empresa recebeu uma pasta com programas "compilados" de fornecedores e precisa saber: **o que existe dentro deles antes de confiar?** Os alvos estão em `material-pratico/pratica4-reversing/alvos/` (gerados por `gerar_alvos.sh`; o código-fonte usado para gerá-los está em `fontes/` — **não olhem antes de tentar pela análise**).
>
> **Regra:** análise **estática apenas**. Não executem nenhum alvo. As ferramentas liberadas: `file`, `strings`, `unzip`, `javap`, `objdump`, `sha256sum`, `cat`, `python3`.

## Missão

Extrair **todas as bandeiras (flags)** escondidas nos alvos e documentar **como** cada uma foi encontrada:

| # | Alvo | O que procurar |
|---|---|---|
| 1 | `segredo.py` | 1 flag |
| 2 | `segredo.pyc` | 1 flag (a compilação escondeu algo?) |
| 3 | `segredo.jar` | 1 flag + 1 senha fictícia |
| 4 | `segredo.exe` | **3 flags** (uma está ofuscada — não aparece no `strings`) |
| 5 | `segredo.elf` | compare com o `.exe` — o que muda? |

Dica de rota: comece pelo `file` em tudo; use `strings` como varredura geral; para o `.jar`, lembre-se de que ele é um ZIP; para a flag ofuscada do `.exe`, procure bytes "estranhos" nas seções de dados com `objdump -s` e decodifique com `python3`.

## Entregáveis do grupo

1. **Tabela** *alvo → flag → ferramenta usada → onde exatamente ela estava* (ex.: "`.exe` → `FLAG{...}` → `strings` → seção `.rdata`").
2. Respostas curtas:
   - a) Por que o `.jar` é mais legível que o `.exe`, se ambos são "compilados"?
   - b) O `.pyc` escondeu a flag? O que isso significa para quem distribui código Python "compilado"?
   - c) A função `segredo_interno()` nunca é chamada pelos programas. Por que ela continua aparecendo no `.jar`/`.exe`/`.pyc`?
   - d) Como vocês decodificaram a flag ofuscada do `.exe`? O que isso prova sobre "ofuscação"?
   - e) Se os programas fossem executados, os segredos apareceriam na tela? Justifique.
   - f) Que risco real existe quando um desenvolvedor embute senhas/chaves em aplicativo? Cite um exemplo de consequência.
3. **Print/captura** de uma descoberta de cada formato (`.py`, `.pyc`, `.jar`, `.exe`).

> Critério: o valor está na **interpretação** (por aquilo existe, o que o formato preserva, qual o risco), não só em achar a flag. Grupo que só listar flags sem explicar = satisfatório, no máximo.

## Tempo

~25 min de análise + discussão guiada pelo professor (Passo 6 do roteiro).
