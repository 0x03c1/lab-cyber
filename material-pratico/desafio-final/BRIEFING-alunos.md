# Desafio — "Incidente na Sertão Digital" (material dos alunos)

> Vocês são a **equipe de resposta a incidentes** da empresa fictícia **Sertão Digital**. Na mesma tarde, três sinais foram reportados. Investiguem as evidências e respondam às perguntas. **Não existe acesso a nenhum sistema externo** — todas as evidências já estão nos arquivos.

## Os três sinais
1. O **serviço web** ficou **lento** e passou a apresentar **falhas** (erros e timeouts).
2. Um **serviço de laboratório** mostrou evidências de **execução remota inesperada**.
3. Uma **estação** registrou **alterações suspeitas na resolução de endereços** (tabela ARP) da rede local.

## Evidências disponíveis (nesta pasta)
| Arquivo | O que é | Como abrir |
|---|---|---|
| `web_access.log` | log de acesso do servidor web | editor de texto / `grep` |
| `web_metrics.csv` | métricas do servidor ao longo do tempo (req/s, latência, CPU, erros) | planilha / editor |
| `recon_services.txt` | reconhecimento de serviços do alvo (estilo `nmap -sV`) | editor de texto |
| `host_events.log` | eventos do host (processos e conexões) | editor de texto |
| `arp_table_before_after.txt` | tabela ARP antes e depois | editor de texto |
| `lab_trafego.pcap` | captura de tráfego (HTTP e HTTPS) | Wireshark / `tshark` |
| `arp_incident.pcap` | captura do incidente de ARP | Wireshark / `tshark` |

Dica de análise das capturas: usem `../pratica3-ettercap/analisar_pcap.sh` ou abram no Wireshark.

## Perguntas a responder
1. Qual **hipótese** explica **cada** sinal?
2. O que **diferencia** DDoS, malware e RCE **neste caso**?
3. Quais **evidências sustentam** e quais **enfraquecem** cada hipótese?
4. Que **informações adicionais** seriam necessárias para confirmar?
5. Qual deve ser a **ordem das ações de contenção**? Justifiquem.
6. Como **restaurar** o ambiente com segurança?
7. Quais **medidas preventivas** recomendam (pelo menos três, justificadas)?

## Entregáveis do grupo
- Diagnóstico técnico de **1 página**.
- **Tabela** relacionando *evidência → hipótese → conclusão*.
- **Plano de resposta** em ordem de prioridade.
- **Três medidas preventivas** justificadas.
- Apresentação oral de **até 3 minutos**.

> Não registrem senhas, dados pessoais ou informações de terceiros. O desafio vale pelo **raciocínio e interpretação**, não pela reprodução de comandos.
