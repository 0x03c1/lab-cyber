# Prática 2 — Roteiro do Metasploit (ciclo identificar → validar → mitigar)

> **Regra absoluta:** apenas contra a VM **Metasploitable 2** (deliberadamente vulnerável), em rede **isolada**, com **autorização**. Nunca contra o Windows real do laboratório ou qualquer sistema de uso cotidiano. Sem persistência, evasão de AV, roubo de credenciais, ransomware ou acesso a terceiros.

> **Por que não há "o comando mágico" pronto aqui:** o nome exato do módulo e os parâmetros **mudam por versão** do Metasploit. O objetivo pedagógico é o aluno **ler os requisitos do módulo** (`show options`) e validar a compatibilidade — não decorar uma linha. A sintaxe canônica é a da documentação oficial do Rapid7/Metasploit e do próprio `info`/`show options`.

Substitua `IP_ALVO` pelo endereço confirmado no reconhecimento (ex.: `192.168.56.40`).

---

## Etapa 1 — Confirmar alvo e autorização (no Kali)
```bash
ping -c 3 IP_ALVO
```
Esperado: resposta. Diga em voz alta e registre: "alvo de laboratório, isolado, autorizado".

## Etapa 2 — Identificar serviços (no Kali)
```bash
./reconhecimento.sh IP_ALVO      # ou: nmap -sV IP_ALVO
```
Anote o serviço/versão foco. Sugestão de laboratório clássico: **FTP `vsftpd 2.3.4`** na porta 21.

## Etapa 3 — Reconhecer a vulnerabilidade
Pela **versão** detectada, consulte a base de vulnerabilidades (notas da imagem Metasploitable, CVE/NVD). Responda com a turma: qual falha? que efeito (RCE?)? pré-condições?

## Etapa 4 — Abrir o Metasploit e INSPECIONAR o módulo (modo análise)
```bash
msfconsole -q
```
Dentro do console (comandos genéricos — o aluno preenche conforme a versão):
```
search <palavra-chave do servico/versao>     # localizar o modulo pertinente
info <caminho/do/modulo>                      # LER: descricao, Targets, requisitos
use  <caminho/do/modulo>
show options                                  # ver parametros com Required = yes
```
**Interprete cada opção `Required=yes` antes de setar qualquer coisa.** Tipicamente aparece `RHOSTS` (alvo), às vezes `RPORT` e um `payload`.

## Etapa 5 — Validar compatibilidade (módulo × serviço × alvo)
Compare a versão da Etapa 2 com os "Targets" listados no `info`.
- **Bate?** siga para a Etapa 6.
- **Não bate?** NÃO force → vá para o **Plano alternativo** (fim deste arquivo).

## Etapa 6 — Demonstração controlada (só se tudo acima for satisfeito)
```
set RHOSTS IP_ALVO
# defina RPORT / payload SOMENTE se 'show options' indicar como obrigatorio
check          # quando suportado: verifica sem explorar
run            # executa a validacao controlada
```
**Payload permitido:** o mínimo para evidenciar execução remota (uma shell de comando simples **no alvo de laboratório**). Nada além disso.

## Etapa 7 — Registrar a evidência (prova de execução remota)
Na sessão aberta, só o suficiente para provar que o comando roda **no alvo**:
```
sysinfo        # ou: getuid / id / hostname, conforme o tipo de sessao
```
Capture a tela/log mostrando o hostname/uid do **alvo** (não da sua estação). **Essa é a evidência.**

## Etapa 8 — Encerrar e restaurar
```
sessions -K        # encerra todas as sessoes
exit
```
No host da VM: **restaurar o snapshot limpo** do Metasploitable.

## Etapa 9 — Correção e validação da mitigação (a parte mais importante)
Explique a correção real:
- **Atualizar/remover** o serviço vulnerável (a versão antiga sai).
- **Reduzir superfície:** desligar serviços não usados.
- **Mínimo privilégio:** o serviço não deveria rodar como root.
- **Segmentação:** o alvo não deve ser alcançável de redes não confiáveis.

**Validar a mitigação:** repetir `nmap -sV IP_ALVO` e o `check` → esperado que a versão mude/o serviço suma ou o `check` reporte "não vulnerável".

---

## Plano alternativo (sem alvo vulnerável, ou módulo incompatível, ou Metasploit não inicia)
Troque a exploração por **reconhecimento + análise**, que avalia o mesmo raciocínio:
```bash
# 1) Reconhecimento de um servico local SEGURO (ex.: o servidor de teste da Pratica 1)
nmap -sV IP_DO_SERVICO_SEGURO

# 2) Analise do que a exposicao significaria, usando o Metasploit em MODO ANALISE:
msfconsole -q
#   search ... ; info ... ; show options        <- SEM 'run'
```
E use a evidência pré-preparada do desafio (`recon_services.txt`, `host_events.log`) para discutir: *se* houvesse exploração, que **sinal** apareceria no host? (Resposta no gabarito: processo filho inesperado + conexão de saída/beacon.)

### Diagnóstico rápido se o Metasploit não iniciar
```bash
msfconsole --version          # a ferramenta responde?
sudo msfdb status             # estado do banco de dados
sudo msfdb init               # inicializa o banco, se necessario
```
Se não resolver em poucos minutos: use os **prints/capturas de referência** e siga em modo análise. A aula **não depende** da exploração ao vivo.
