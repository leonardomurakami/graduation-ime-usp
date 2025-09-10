import java.io.*;
import java.util.*;

public class Programa4 {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("Uso: java Programa4 <arquivo_codigo_latex> <arquivo_tabela_simbolos>");
            System.exit(1);
        }
        
        try {
            // carrega a tabela de simbolos (latex -> letra)
            Map<String, Character> tabelaSimbolos = carregarTabelaSimbolos(args[1]);
            
            // le o arquivo com codigos latex e pontos
            String textoCodeado = lerArquivo(args[0]);
            
            // decodifica a mensagem
            String mensagemDecodificada = decodificar(textoCodeado, tabelaSimbolos);
            
            // imprime o resultado
            System.out.println(mensagemDecodificada);
            
        } catch (IOException e) {
            System.err.println("Erro ao ler arquivos: " + e.getMessage());
            System.exit(1);
        }
    }
    
    private static Map<String, Character> carregarTabelaSimbolos(String nomeArquivo) throws IOException {
        Map<String, Character> tabela = new HashMap<>();
        
        try (BufferedReader br = new BufferedReader(new FileReader(nomeArquivo))) {
            String linha;
            while ((linha = br.readLine()) != null) {
                linha = linha.trim();
                if (!linha.isEmpty()) {
                    // formato esperado: "a $\natural$"
                    String[] partes = linha.split("\\s+", 2);
                    if (partes.length == 2) {
                        char letra = partes[0].charAt(0);
                        String codigoLatex = partes[1];
                        tabela.put(codigoLatex, letra);
                    }
                }
            }
        }
        
        return tabela;
    }
    
    private static String lerArquivo(String nomeArquivo) throws IOException {
        StringBuilder conteudo = new StringBuilder();
        
        try (BufferedReader br = new BufferedReader(new FileReader(nomeArquivo))) {
            String linha;
            while ((linha = br.readLine()) != null) {
                conteudo.append(linha);
            }
        }
        
        return conteudo.toString();
    }
    
    private static String decodificar(String textoCodeado, Map<String, Character> tabelaSimbolos) {
        StringBuilder resultado = new StringBuilder();
        
        int i = 0;
        while (i < textoCodeado.length()) {
            if (textoCodeado.charAt(i) == '.') {
                // ponto vira espaco
                resultado.append(' ');
                i++;
            } else if (textoCodeado.charAt(i) == '$') {
                // encontrou inicio de codigo latex
                int fimCodigo = textoCodeado.indexOf('$', i + 1);
                if (fimCodigo != -1) {
                    String codigoLatex = textoCodeado.substring(i, fimCodigo + 1);
                    Character letra = tabelaSimbolos.get(codigoLatex);
                    if (letra != null) {
                        resultado.append(letra);
                    } else {
                        // se nao encontrar na tabela, mantem o codigo original
                        resultado.append(codigoLatex);
                    }
                    i = fimCodigo + 1;
                } else {
                    // $ sem fechamento, adiciona como esta
                    resultado.append(textoCodeado.charAt(i));
                    i++;
                }
            } else {
                // outros caracteres (nao deveria acontecer segundo as especificacoes)
                resultado.append(textoCodeado.charAt(i));
                i++;
            }
        }
        
        return resultado.toString();
    }
}