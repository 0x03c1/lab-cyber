#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor HTTP de TESTE para a Pratica 1 (DDoS / disponibilidade).
Pura biblioteca padrao. Serve para medir disponibilidade sob carga CONTROLADA
e LOCAL. Nao expor na internet.

Endpoints:
    GET /          -> resposta rapida (linha de base)
    GET /status    -> resposta rapida com texto simples
    GET /relatorio -> endpoint PROPOSITALMENTE "caro" (simula trabalho de
                      aplicacao: um pouco de CPU + espera). Use-o para ver a
                      latencia subir sob concorrencia, como num ataque de
                      camada de aplicacao.

Uso (no Pi ou no Kali, usuario comum):
    python3 servidor_teste.py                 # escuta em 0.0.0.0:8000
    python3 servidor_teste.py --port 8080
    python3 servidor_teste.py --host 127.0.0.1

Pare com Ctrl+C.
"""
import argparse
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def _responder(self, corpo: bytes, status=200, ctype="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        caminho = self.path.split("?", 1)[0]
        if caminho in ("/", "/status"):
            self._responder(b"status=ok servico=sertao-digital-TESTE\n")
        elif caminho == "/relatorio":
            # Trabalho "caro" proposital: soma + pequena espera.
            # Mostra como poucos endpoints pesados saturam sob concorrencia.
            inicio = time.time()
            total = 0
            for i in range(200_000):
                total += i * i
            time.sleep(0.05)
            dur = (time.time() - inicio) * 1000
            self._responder(f"relatorio gerado em {dur:.1f} ms (trabalho sintetico)\n".encode())
        else:
            self._responder(b"nao encontrado\n", status=404)

    # Silencia o log padrao barulhento; deixamos o monitoramento por conta do script.
    def log_message(self, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Servidor de TESTE ouvindo em http://{args.host}:{args.port}")
    print("Endpoints: /  /status  /relatorio   | Ctrl+C para parar")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor interrompido.")
        srv.server_close()


if __name__ == "__main__":
    main()
