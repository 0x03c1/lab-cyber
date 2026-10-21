"""segredo.py - alvo INTERPRETADO da Pratica 4 (engenharia reversa).

Nao e malware: apenas imprime uma mensagem. Os "segredos" existem
SOMENTE para os alunos extrarem. A comparacao com o .pyc compilado
a partir DESTE arquivo e o ponto didatico: interpretado nao esconde
nada, e nem bytecode "esconde" strings.
"""

FLAG_PY = "FLAG{py_codigo_aberto}"
SENHA_FICTICIA = "python-senha-lab"


def segredo_interno():
    """Funcao nunca chamada - continua visivel ate no .pyc."""
    return FLAG_PY + " / " + SENHA_FICTICIA


if __name__ == "__main__":
    print("Script benigno do lab. Nada a ver aqui.")
