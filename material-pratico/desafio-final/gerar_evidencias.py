#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de EVIDÊNCIAS SINTÉTICAS para o desafio "Incidente na Sertão Digital".

Tudo aqui é FICTÍCIO e SEM alcance externo. Não há credenciais reais, dados
pessoais, nem endereços de produção. A rede usada (192.168.56.0/24) é a faixa
host-only padrão do VirtualBox, apropriada para laboratório isolado.

Uso:
    python3 gerar_evidencias.py            # gera tudo no diretório atual
    python3 gerar_evidencias.py --out DIR  # gera em DIR

Produz:
    web_access.log            log de acesso do servidor web (base + sobrecarga)
    web_metrics.csv           métricas do servidor ao longo do tempo
    recon_services.txt        saída (estilo nmap -sV) do serviço de laboratório
    host_events.log           eventos do host: processo filho + beacon de saída
    arp_table_before_after.txt tabela ARP antes/depois (MAC duplicado)
    lab_trafego.pcap          HTTP em texto claro vs TLS cifrado (p/ Prática 3)
    arp_incident.pcap         envenenamento de cache ARP (p/ desafio/Prática 3)

Os .pcap são escritos com a biblioteca padrão (sem scapy). Abra no Wireshark
ou leia com tshark (ver analisar_pcap.sh).
"""
import argparse
import os
import random
import struct
from datetime import datetime, timedelta

# --------------------------------------------------------------------------
# Premissas do laboratório (ajuste se a sua rede for diferente)
# --------------------------------------------------------------------------
REDE          = "192.168.56"
IP_GATEWAY    = f"{REDE}.1"
IP_ESTACAO    = f"{REDE}.30"    # estação da vítima (Windows/análise)
IP_ALVO       = f"{REDE}.40"    # serviço de laboratório (Metasploitable)
IP_ATACANTE   = f"{REDE}.50"    # host do atacante (sintético)

MAC_GATEWAY   = "aa:bb:cc:00:00:01"
MAC_ESTACAO   = "aa:bb:cc:00:00:30"
MAC_ALVO      = "aa:bb:cc:00:00:40"
MAC_ATACANTE  = "de:ad:be:ef:00:50"   # MAC do atacante (fácil de reconhecer)

random.seed(42)  # determinístico: todos os grupos recebem as mesmas evidências

# IPs "de origem" fictícios para simular a dispersão de um DDoS na camada de aplicação
BOTS = [f"203.0.113.{i}" for i in range(2, 60)]  # 203.0.113.0/24 é faixa de DOCUMENTAÇÃO (TEST-NET-3)
CLIENTES_LEGITIMOS = [f"198.51.100.{i}" for i in (10, 11, 12, 13, 14)]  # 198.51.100.0/24 também é doc.

# ==========================================================================
# 1) web_access.log  +  2) web_metrics.csv
# ==========================================================================
def gerar_web(out):
    """
    Janela de 10 minutos. Minutos 0-3: tráfego normal e baixo. Minuto 4: começa
    uma sobrecarga na CAMADA DE APLICAÇÃO (muitas origens batendo em /relatorio,
    endpoint caro) -> latência sobe, CPU satura, surgem 503/timeout. Minuto 8:
    volta ao normal (mitigação por rate limiting).
    """
    t0 = datetime(2026, 10, 21, 14, 0, 0)
    acc = []
    met = ["timestamp,req_por_seg,latencia_ms_p95,cpu_pct,mem_pct,taxa_erro_pct"]

    def linha_acesso(ts, ip, metodo, caminho, status, tam, ms):
        # formato combined-like, suficiente para análise didática
        return (f'{ip} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
                f'"{metodo} {caminho} HTTP/1.1" {status} {tam} "-" "curl/8.0" {ms}ms')

    for minuto in range(10):
        ataque = 4 <= minuto < 8
        for seg in range(0, 60, 5):  # amostra a cada 5s
            ts = t0 + timedelta(minutes=minuto, seconds=seg)
            if ataque:
                rps = random.randint(180, 240)
                lat = random.randint(1800, 4200)
                cpu = random.randint(92, 100)
                mem = random.randint(70, 85)
                err = random.randint(35, 60)
            else:
                rps = random.randint(3, 12)
                lat = random.randint(20, 90)
                cpu = random.randint(5, 25)
                mem = random.randint(40, 55)
                err = 0 if random.random() > 0.2 else random.randint(0, 2)
            met.append(f"{ts.strftime('%Y-%m-%d %H:%M:%S')},{rps},{lat},{cpu},{mem},{err}")

            # algumas linhas de acesso representativas por amostra
            if ataque:
                for _ in range(6):
                    ip = random.choice(BOTS)
                    ms = random.randint(1500, 5000)
                    status = random.choice([200, 503, 503, 504, 502])
                    tam = 0 if status >= 500 else random.randint(500, 2000)
                    acc.append(linha_acesso(ts, ip, "GET", "/relatorio?export=full", status, tam, ms))
            else:
                for _ in range(2):
                    ip = random.choice(CLIENTES_LEGITIMOS)
                    ms = random.randint(15, 120)
                    acc.append(linha_acesso(ts, ip, "GET", random.choice(["/", "/status", "/produtos"]),
                                            200, random.randint(400, 1500), ms))

    with open(os.path.join(out, "web_access.log"), "w") as f:
        f.write("\n".join(acc) + "\n")
    with open(os.path.join(out, "web_metrics.csv"), "w") as f:
        f.write("\n".join(met) + "\n")


# ==========================================================================
# 3) recon_services.txt  (estilo "nmap -sV" do serviço de laboratório)
# ==========================================================================
def gerar_recon(out):
    txt = f"""# Resultado SINTÉTICO de reconhecimento do serviço de laboratório.
# Reproduz o estilo de 'nmap -sV {IP_ALVO}' contra um alvo deliberadamente
# vulnerável (Metasploitable 2). NÃO foi executado contra sistema real.

Starting Nmap ( https://nmap.org ) contra {IP_ALVO}
Nmap scan report for {IP_ALVO}
Host is up (0.00042s latency).
Not shown: 977 closed tcp ports (reset)

PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 2.3.4
22/tcp   open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
23/tcp   open  telnet      Linux telnetd
25/tcp   open  smtp        Postfix smtpd
80/tcp   open  http        Apache httpd 2.2.8 ((Ubuntu) DAV/2)
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X
445/tcp  open  netbios-ssn Samba smbd 3.X - 4.X
3306/tcp open  mysql       MySQL 5.0.51a-3ubuntu5
5900/tcp open  vnc         VNC (protocol 3.3)

MAC Address: {MAC_ALVO.upper().replace(':','-')} (Laboratorio-Sintetico)
Service Info: OS: Linux (laboratorio isolado)

# OBSERVACAO PARA O PROFESSOR:
# - A porta 21 expoe 'vsftpd 2.3.4', versao com vulnerabilidade de laboratorio
#   amplamente DOCUMENTADA e usada para ensino de RCE. E o foco sugerido da Pratica 2.
# - Superficie de ataque: muitos servicos abertos e versoes antigas = risco.
"""
    with open(os.path.join(out, "recon_services.txt"), "w") as f:
        f.write(txt)


# ==========================================================================
# 4) host_events.log  (RCE -> processo filho inesperado + beacon de saida)
# ==========================================================================
def gerar_host_events(out):
    t0 = datetime(2026, 10, 21, 14, 4, 30)
    linhas = [
        "# Eventos SINTETICOS da estacao/servico de laboratorio (nivel didatico).",
        "# Mostram um servico de rede gerando um processo filho inesperado e um",
        "# 'beacon' periodico de saida (comportamento tipico pos-RCE). Tudo ficticio.",
        "",
    ]
    def ev(dt, msg):
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} labhost {msg}"

    linhas += [
        ev(t0, "ftpd[1821]: conexao recebida de " + IP_ATACANTE + " na porta 21"),
        ev(t0 + timedelta(seconds=2), "ftpd[1821]: comando de autenticacao malformado recebido"),
        ev(t0 + timedelta(seconds=3), "kernel: ftpd(1821) gerou processo filho inesperado: /bin/sh (pid 1840)"),
        ev(t0 + timedelta(seconds=3), "sh[1840]: processo shell iniciado com uid=0(root)  <-- ANOMALIA: servico FTP nao deveria abrir shell"),
        ev(t0 + timedelta(seconds=5), f"network: nova conexao de SAIDA {IP_ALVO}:40141 -> {IP_ATACANTE}:4444 (estado ESTABELECIDO)"),
    ]
    # beacons periodicos
    for i in range(1, 6):
        dt = t0 + timedelta(seconds=5 + i * 30)
        linhas.append(ev(dt, f"network: beacon de SAIDA {IP_ALVO} -> {IP_ATACANTE}:4444 (keep-alive, {random.randint(60,120)} bytes)"))
    linhas += [
        ev(t0 + timedelta(seconds=200), "cron: NOVA tarefa agendada criada por uid=0: '* * * * * /tmp/.svc'  <-- possivel PERSISTENCIA"),
        ev(t0 + timedelta(seconds=205), "auth: nenhuma falha de login registrada neste intervalo (acesso veio por execucao remota, nao por senha)"),
        "",
    ]
    with open(os.path.join(out, "host_events.log"), "w") as f:
        f.write("\n".join(linhas) + "\n")


# ==========================================================================
# 5) arp_table_before_after.txt
# ==========================================================================
def gerar_arp_txt(out):
    txt = f"""# Tabela ARP da estacao {IP_ESTACAO} ANTES e DEPOIS do incidente (sintetico).
# Comando de referencia: 'arp -a' (Windows) ou 'ip neigh' (Linux).

==================== ANTES (estado normal) ====================
{IP_GATEWAY:<16} {MAC_GATEWAY}   dinamico
{IP_ALVO:<16} {MAC_ALVO}   dinamico

==================== DEPOIS (estado suspeito) ====================
{IP_GATEWAY:<16} {MAC_ATACANTE}   dinamico     <-- O MAC do GATEWAY MUDOU
{IP_ALVO:<16} {MAC_ALVO}   dinamico
{IP_ATACANTE:<16} {MAC_ATACANTE}   dinamico     <-- mesmo MAC do 'gateway' acima = MAC DUPLICADO

# SINAL-CHAVE: o IP do gateway ({IP_GATEWAY}) passou a responder com o MAC
# {MAC_ATACANTE}, que tambem pertence a {IP_ATACANTE}. Dois IPs, um unico MAC:
# classico de ENVENENAMENTO DE CACHE ARP (man-in-the-middle). O trafego da
# estacao para o 'gateway' passa a ir para o atacante.
"""
    with open(os.path.join(out, "arp_table_before_after.txt"), "w") as f:
        f.write(txt)


# ==========================================================================
# Utilidades de rede para escrever .pcap SEM scapy (so struct)
# ==========================================================================
def mac_bytes(mac):
    return bytes(int(x, 16) for x in mac.split(":"))

def ip_bytes(ip):
    return bytes(int(x) for x in ip.split("."))

def checksum(data):
    if len(data) % 2:
        data += b"\x00"
    s = 0
    for i in range(0, len(data), 2):
        s += (data[i] << 8) + data[i + 1]
    s = (s >> 16) + (s & 0xFFFF)
    s += (s >> 16)
    return (~s) & 0xFFFF

def eth(dst, src, ethertype):
    return mac_bytes(dst) + mac_bytes(src) + struct.pack(">H", ethertype)

def ipv4(src, dst, proto, payload, ident=0):
    ver_ihl = 0x45
    tos = 0
    total_len = 20 + len(payload)
    flags_frag = 0x4000
    ttl = 64
    hdr = struct.pack(">BBHHHBBH4s4s", ver_ihl, tos, total_len, ident,
                      flags_frag, ttl, proto, 0, ip_bytes(src), ip_bytes(dst))
    chk = checksum(hdr)
    hdr = struct.pack(">BBHHHBBH4s4s", ver_ihl, tos, total_len, ident,
                      flags_frag, ttl, proto, chk, ip_bytes(src), ip_bytes(dst))
    return hdr + payload

def tcp(src_ip, dst_ip, sport, dport, seq, ack, flags, payload=b""):
    offset = (5 << 4)
    window = 64240
    hdr_wo_chk = struct.pack(">HHIIBBHHH", sport, dport, seq, ack, offset, flags, window, 0, 0)
    pseudo = ip_bytes(src_ip) + ip_bytes(dst_ip) + struct.pack(">BBH", 0, 6, len(hdr_wo_chk) + len(payload))
    chk = checksum(pseudo + hdr_wo_chk + payload)
    hdr = struct.pack(">HHIIBBHHH", sport, dport, seq, ack, offset, flags, window, chk, 0)
    return hdr + payload

def udp(src_ip, dst_ip, sport, dport, payload=b""):
    length = 8 + len(payload)
    hdr = struct.pack(">HHHH", sport, dport, length, 0)  # checksum 0 (opcional em IPv4)
    return hdr + payload

def arp(oper, sha, spa, tha, tpa):
    # htype=1 (ethernet), ptype=0x0800 (IPv4), hlen=6, plen=4
    return struct.pack(">HHBBH", 1, 0x0800, 6, 4, oper) + \
           mac_bytes(sha) + ip_bytes(spa) + mac_bytes(tha) + ip_bytes(tpa)

class Pcap:
    def __init__(self):
        self.pkts = []  # (ts, bytes)
        self.ts = 1_761_055_200.0  # epoch sintetico fixo (21/10/2026 ~14:00 UTC)
    def add(self, frame, dt=0.01):
        self.ts += dt
        self.pkts.append((self.ts, frame))
    def write(self, path):
        with open(path, "wb") as f:
            # global header: magic, v2.4, zone0, sig0, snaplen, LINKTYPE_ETHERNET(1)
            f.write(struct.pack(">IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
            for ts, frame in self.pkts:
                sec = int(ts)
                usec = int((ts - sec) * 1_000_000)
                f.write(struct.pack(">IIII", sec, usec, len(frame), len(frame)))
                f.write(frame)


# ==========================================================================
# 6) lab_trafego.pcap  (HTTP em texto claro  vs  TLS cifrado)
# ==========================================================================
def gerar_lab_trafego(out):
    p = Pcap()
    FIN, SYN, RST, PSH, ACK = 0x01, 0x02, 0x04, 0x08, 0x10

    # --- ARP normal: estacao pergunta quem e o gateway ---
    p.add(eth("ff:ff:ff:ff:ff:ff", MAC_ESTACAO, 0x0806) +
          arp(1, MAC_ESTACAO, IP_ESTACAO, "00:00:00:00:00:00", IP_GATEWAY))
    p.add(eth(MAC_ESTACAO, MAC_GATEWAY, 0x0806) +
          arp(2, MAC_GATEWAY, IP_GATEWAY, MAC_ESTACAO, IP_ESTACAO))

    # --- Handshake TCP para a porta 80 (HTTP) ---
    seq_c, seq_s = 1000, 5000
    p.add(eth(MAC_ALVO, MAC_ESTACAO, 0x0800) + ipv4(IP_ESTACAO, IP_ALVO, 6, tcp(IP_ESTACAO, IP_ALVO, 49200, 80, seq_c, 0, SYN)))
    p.add(eth(MAC_ESTACAO, MAC_ALVO, 0x0800) + ipv4(IP_ALVO, IP_ESTACAO, 6, tcp(IP_ALVO, IP_ESTACAO, 80, 49200, seq_s, seq_c + 1, SYN | ACK)))
    p.add(eth(MAC_ALVO, MAC_ESTACAO, 0x0800) + ipv4(IP_ESTACAO, IP_ALVO, 6, tcp(IP_ESTACAO, IP_ALVO, 49200, 80, seq_c + 1, seq_s + 1, ACK)))

    # --- HTTP GET em TEXTO CLARO (observavel!) ---
    req = (b"GET /status HTTP/1.1\r\n"
           b"Host: sertao-digital.lab\r\n"
           b"User-Agent: curl/8.0\r\n"
           b"X-Demo-Token: LAB-SINTETICO-123\r\n"   # token FICTICIO, so para mostrar o risco do texto claro
           b"\r\n")
    p.add(eth(MAC_ALVO, MAC_ESTACAO, 0x0800) + ipv4(IP_ESTACAO, IP_ALVO, 6, tcp(IP_ESTACAO, IP_ALVO, 49200, 80, seq_c + 1, seq_s + 1, PSH | ACK, req)))
    resp = (b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 31\r\n"
            b"\r\n"
            b"status=ok servico=sertao-digital")
    p.add(eth(MAC_ESTACAO, MAC_ALVO, 0x0800) + ipv4(IP_ALVO, IP_ESTACAO, 6, tcp(IP_ALVO, IP_ESTACAO, 80, 49200, seq_s + 1, seq_c + 1 + len(req), PSH | ACK, resp)))

    # --- Handshake TCP para a porta 443 (HTTPS) ---
    seq_c2, seq_s2 = 2000, 9000
    p.add(eth(MAC_ALVO, MAC_ESTACAO, 0x0800) + ipv4(IP_ESTACAO, IP_ALVO, 6, tcp(IP_ESTACAO, IP_ALVO, 49222, 443, seq_c2, 0, SYN)))
    p.add(eth(MAC_ESTACAO, MAC_ALVO, 0x0800) + ipv4(IP_ALVO, IP_ESTACAO, 6, tcp(IP_ALVO, IP_ESTACAO, 443, 49222, seq_s2, seq_c2 + 1, SYN | ACK)))
    p.add(eth(MAC_ALVO, MAC_ESTACAO, 0x0800) + ipv4(IP_ESTACAO, IP_ALVO, 6, tcp(IP_ESTACAO, IP_ALVO, 49222, 443, seq_c2 + 1, seq_s2 + 1, ACK)))

    # --- TLS ClientHello / ServerHello: conteudo CIFRADO (nao legivel) ---
    # Registro TLS: tipo 0x16 (handshake), versao 0x0301/0x0303, len, corpo (bytes opacos)
    client_hello = b"\x16\x03\x01\x00\x30" + bytes(random.randint(0, 255) for _ in range(0x30))
    server_hello = b"\x16\x03\x03\x00\x30" + bytes(random.randint(0, 255) for _ in range(0x30))
    p.add(eth(MAC_ALVO, MAC_ESTACAO, 0x0800) + ipv4(IP_ESTACAO, IP_ALVO, 6, tcp(IP_ESTACAO, IP_ALVO, 49222, 443, seq_c2 + 1, seq_s2 + 1, PSH | ACK, client_hello)))
    p.add(eth(MAC_ESTACAO, MAC_ALVO, 0x0800) + ipv4(IP_ALVO, IP_ESTACAO, 6, tcp(IP_ALVO, IP_ESTACAO, 443, 49222, seq_s2 + 1, seq_c2 + 1 + len(client_hello), PSH | ACK, server_hello)))

    p.write(os.path.join(out, "lab_trafego.pcap"))


# ==========================================================================
# 7) arp_incident.pcap  (envenenamento de cache ARP)
# ==========================================================================
def gerar_arp_incident(out):
    p = Pcap()
    # Trafego ARP normal inicial
    p.add(eth("ff:ff:ff:ff:ff:ff", MAC_ESTACAO, 0x0806) +
          arp(1, MAC_ESTACAO, IP_ESTACAO, "00:00:00:00:00:00", IP_GATEWAY), dt=0.5)
    p.add(eth(MAC_ESTACAO, MAC_GATEWAY, 0x0806) +
          arp(2, MAC_GATEWAY, IP_GATEWAY, MAC_ESTACAO, IP_ESTACAO), dt=0.01)

    # ATAQUE: o atacante envia respostas ARP nao solicitadas (gratuitous),
    # afirmando que o IP do GATEWAY esta no MAC do ATACANTE. Repetido para
    # manter o cache envenenado.
    for _ in range(5):
        # para a vitima: "o gateway sou eu"
        p.add(eth(MAC_ESTACAO, MAC_ATACANTE, 0x0806) +
              arp(2, MAC_ATACANTE, IP_GATEWAY, MAC_ESTACAO, IP_ESTACAO), dt=1.0)
        # para o gateway: "a vitima sou eu" (MITM completo nos dois sentidos)
        p.add(eth(MAC_GATEWAY, MAC_ATACANTE, 0x0806) +
              arp(2, MAC_ATACANTE, IP_ESTACAO, MAC_GATEWAY, IP_GATEWAY), dt=0.02)

    p.write(os.path.join(out, "arp_incident.pcap"))


# ==========================================================================
def main():
    ap = argparse.ArgumentParser(description="Gera evidencias sinteticas do desafio.")
    ap.add_argument("--out", default=".", help="diretorio de saida (padrao: atual)")
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)

    gerar_web(out)
    gerar_recon(out)
    gerar_host_events(out)
    gerar_arp_txt(out)
    gerar_lab_trafego(out)
    gerar_arp_incident(out)

    print("Evidencias sinteticas geradas em:", os.path.abspath(out))
    for nome in ["web_access.log", "web_metrics.csv", "recon_services.txt",
                 "host_events.log", "arp_table_before_after.txt",
                 "lab_trafego.pcap", "arp_incident.pcap"]:
        caminho = os.path.join(out, nome)
        if os.path.exists(caminho):
            print(f"  [ok] {nome:<28} ({os.path.getsize(caminho)} bytes)")


if __name__ == "__main__":
    main()
