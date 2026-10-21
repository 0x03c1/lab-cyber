/* segredo.c - alvo BENIGNO da Pratica 4 (engenharia reversa).
   Nao e malware: apenas imprime uma mensagem. Os "segredos" (flags e
   senha ficticia) existem SOMENTE para os alunos extrarem por analise
   estatica. NUNCA execute este binario fora de laboratorio isolado;
   nesta pratica ele nem precisa ser executado. */
#include <stdio.h>

/* FLAG_EXE_1: fica visivel direto no 'strings' (secao .rdata) */
static const char *FLAG_EXE = "FLAG{exe_strings_facil}";

/* FLAG_EXE_2: dentro de funcao NUNCA chamada (dead code) -
   compiladores sem otimizacao mantem o codigo inteiro no binario */
static void segredo_interno(void) {
    const char *segredo = "FLAG{exe_dead_code}";
    const char *senha_ficticia = "SenhaForte123";
    printf("%s %s\n", segredo, senha_ficticia);
}

/* FLAG_EXE_3: ofuscada com XOR 0x42 - 'strings' mostra lixo,
   so o 'objdump -s' + decodificacao revela */
static const unsigned char SEGREDO_XOR[] = {
    0x04, 0x0e, 0x03, 0x05, 0x39, 0x27, 0x3a, 0x27,
    0x1d, 0x3a, 0x2d, 0x30, 0x1d, 0x76, 0x70, 0x3f
};

static void decodifica(void) {
    char buf[sizeof(SEGREDO_XOR) + 1];
    for (unsigned i = 0; i < sizeof(SEGREDO_XOR); i++)
        buf[i] = SEGREDO_XOR[i] ^ 0x42;
    buf[sizeof(SEGREDO_XOR)] = '\0';
    printf("%s\n", buf);
}

int main(void) {
    printf("Programa benigno do lab. Nada a ver aqui.\n");
    (void)FLAG_EXE;
    (void)segredo_interno;
    (void)decodifica;
    return 0;
}
