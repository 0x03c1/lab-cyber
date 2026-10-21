/* Segredo.java - alvo BENIGNO da Pratica 4 (engenharia reversa).
   Nao e malware: apenas imprime uma mensagem. Os "segredos" existem
   SOMENTE para os alunos extrarem por analise estatica. */
public class Segredo {

    /* FLAG_JAR_1: constante da classe - vai inteira para o .class */
    private static final String FLAG_JAR = "FLAG{jar_javap_legivel}";

    /* credencial ficticia embutida (mesmo padrao de incidentes reais) */
    private static final String SENHA_FICTICIA = "senha-lab-123";

    public static void main(String[] args) {
        System.out.println("Aplicativo benigno do lab. Nada a ver aqui.");
    }

    /* FLAG_JAR_2: metodo NUNCA chamado - bytecode inteiro vai no .jar */
    public static String segredoInterno() {
        return FLAG_JAR + " / " + SENHA_FICTICIA;
    }
}
