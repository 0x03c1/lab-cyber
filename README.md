# Aula prática de Cibersegurança — DDoS · Malware · RCE

Pacote pronto para executar. O plano completo da aula (teoria, rubrica e
checklists) está em `aula-ciberseguranca-ddos-malware-rce.md`, aqui na raiz.
**Tudo é sintético e para rede isolada.**

## Mapa do repositório
```
.
├── README.md                                  <- este guia (ordem de execução)
├── aula-ciberseguranca-ddos-malware-rce.md    <- plano completo da aula
└── material-pratico/
    ├── pratica1-ddos/
    │   ├── servidor_teste.py          servidor HTTP de teste (roda no Pi ou Kali)
    │   ├── medir_baseline.sh          mede tempo de resposta ANTES (estação cliente)
    │   ├── carga_controlada.sh        carga pequena/interrompível (hey ou ab)
    │   └── monitorar_recursos.sh      CPU/mem/conexões DO servidor durante a carga
    ├── pratica2-rce/
    │   ├── reconhecimento.sh          nmap -sV do alvo de laboratório
    │   └── roteiro-metasploit.md      ciclo identificar→validar→mitigar (comentado)
    ├── pratica3-ettercap/
    │   ├── analisar_pcap.sh           HTTP-claro vs TLS-cifrado + ARP envenenado
    │   └── ver_arp.sh                 tabela ARP atual + destaque de MAC duplicado
    ├── desafio-final/
    │   ├── gerar_evidencias.py        (re)gera todas as evidências sintéticas
    │   ├── BRIEFING-alunos.md         enunciado + lista de evidências (p/ alunos)
    │   ├── GABARITO-professor.md      respostas comentadas (SÓ local - fora do repositório)
    │   ├── web_access.log  web_metrics.csv  recon_services.txt
    │   ├── host_events.log  arp_table_before_after.txt
    │   └── lab_trafego.pcap  arp_incident.pcap
    └── folha-registro/
        └── folha-de-registro.md       folha dos grupos (imprimir)
```

## Premissas de rede (ajuste e confirme)
Padrão usado nas evidências: faixa isolada **`192.168.56.0/24`** (host-only do VirtualBox).
- Gateway `.1` · Estação `.30` · **Alvo vulnerável `.40`** · Atacante (sintético) `.50`
- Estação do professor (Pi/servidor de teste): use um IP livre, ex.: `.10`.

Se sua rede for outra, edite as constantes no topo de `material-pratico/desafio-final/gerar_evidencias.py` e **regenere** (`python3 gerar_evidencias.py`), além de passar o IP certo aos scripts.

## Antes da aula (5 min de checagem)
```bash
# no host da estação do professor
uname -m            # Pi deve mostrar aarch64 (ARM64) -> NÃO roda VM x86
ip addr; ip route   # anote o IP; confirme que a rede está isolada
nmap --version; tshark --version
# gerador de carga: tenha 'hey' OU 'ab' (apache2-utils) em alguma estação
```
As evidências do desafio **já estão geradas** em `material-pratico/desafio-final/`. Para recriá-las:
```bash
cd material-pratico/desafio-final && python3 gerar_evidencias.py
```

---

## Ordem de execução na aula

### Prática 1 — DDoS / disponibilidade (~15 min)
**No servidor (Pi ou Kali):**
```bash
cd material-pratico/pratica1-ddos
python3 servidor_teste.py                 # fica rodando; anote o IP do host
# em outra aba DO SERVIDOR:
./monitorar_recursos.sh 8000
```
**Na estação cliente:**
```bash
cd material-pratico/pratica1-ddos
./medir_baseline.sh  <IP_SERVIDOR> 8000 /status      # linha de base
./carga_controlada.sh <IP_SERVIDOR> 8000 /relatorio 200 10   # carga
./medir_baseline.sh  <IP_SERVIDOR> 8000 /relatorio   # comparar DURANTE
```
Observe: latência sobe? aparecem falhas? CPU satura? → discutir teste legítimo × DDoS.
**Parar:** `Ctrl+C` no cliente e no servidor.

### Prática 2 — RCE com Metasploit (~20 min)
```bash
cd material-pratico/pratica2-rce
./reconhecimento.sh <IP_ALVO>        # ex.: 192.168.56.40
# depois siga roteiro-metasploit.md passo a passo
```
Sem alvo vivo? Use o **plano alternativo** do roteiro + `material-pratico/desafio-final/recon_services.txt` e `host_events.log`.

### Prática 3 — Interceptação / Ettercap (~15 min)
```bash
cd material-pratico/pratica3-ettercap
./analisar_pcap.sh ../desafio-final      # HTTP-claro vs TLS + ARP envenenado
./ver_arp.sh                              # tabela ARP da máquina (Windows: arp -a)
```
Demonstração ao vivo do Ettercap é **opcional** e só em rede isolada com tráfego sintético (ver seção 8 do plano). Se a interface não aparecer, fique na análise de `.pcap`.

### Desafio final — "Sertão Digital" (~25 min + apresentações)
1. Entregue aos grupos o `material-pratico/desafio-final/BRIEFING-alunos.md` e as evidências (tudo em `material-pratico/desafio-final/`, **exceto** o `GABARITO`).
2. Grupos analisam com editor de texto, planilha, Wireshark e `analisar_pcap.sh`.
3. Correção com `material-pratico/desafio-final/GABARITO-professor.md` (arquivo local do professor, fora do repositório) e rubrica (seção 13 do plano).

---

## Encerramento
Siga o **Checklist de encerramento** (seção 14 do plano): parar servidor/carga, restaurar snapshot do alvo, conferir ARP normal, arquivar evidências/folhas, segregar a rede. Lembre: os `.pcap`/logs aqui são sintéticos; podem ficar para reuso.

## Regras de segurança (valem para toda a aula)
- Rede **isolada**; nunca testar endereços públicos ou de terceiros.
- Carga **pequena**, autorizada e interrompível; parar imediatamente se houver degradação inesperada.
- Exploração **só** no alvo de laboratório; sem persistência, evasão, roubo de credenciais ou ransomware.
- A aula **não depende** de exploração bem-sucedida — a avaliação é pela investigação e interpretação.
