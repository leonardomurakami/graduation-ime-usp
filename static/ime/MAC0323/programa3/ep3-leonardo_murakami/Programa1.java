import java.io.*;
import java.util.*;

public class Programa1 {
    
    // tabela de simbolos inicializada vazia
    private static Map<Character, String> symbolTable = new HashMap<>();
    
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Uso: java Programa1 <arquivo_tabela_simbolos.txt> <arquivo_entrada.txt>");
            return;
        }
        
        String symbolTableFile = args[0];
        String inputFile = args[1];
        
        // carrega tabela de simbolos
        loadSymbolTable(symbolTableFile);
        
        try {
            String inputText = readFile(inputFile);
            String encodedText = encodeText(inputText);
            System.out.println(encodedText);
        } catch (IOException e) {
            System.err.println("Erro ao ler arquivo: " + e.getMessage());
        }
    }
    
    // le o conteudo de um arquivo e retorna como string
    private static String readFile(String filename) throws IOException {
        StringBuilder content = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line);
                content.append(" "); // adiciona espaco entre linhas
            }
        }
        return content.toString().trim();
    }
    
    // carrega tabela de simbolos de um arquivo
    // formato esperado: cada linha deve ter "letra codigo_latex"
    private static void loadSymbolTable(String filename) {
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.length() > 0) {
                    String[] parts = line.split("\\s+", 2);
                    if (parts.length == 2) {
                        char key = parts[0].charAt(0);
                        String latexCode = parts[1];
                        symbolTable.put(key, latexCode);
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("Erro ao carregar tabela de símbolos: " + e.getMessage());
            System.exit(1);
        }
    }
    
    // codifica o texto usando a tabela de simbolos
    // espacos sao convertidos para pontos
    private static String encodeText(String text) {
        StringBuilder encoded = new StringBuilder();
        
        for (char c : text.toCharArray()) {
            if (c == ' ') {
                encoded.append(".");
            } else if (Character.isLetter(c)) {
                char lowerC = Character.toLowerCase(c);
                String symbol = symbolTable.get(lowerC);
                if (symbol != null) {
                    encoded.append(symbol);
                } else {
                    // se nao encontrar simbolo, mantem o caractere original
                    encoded.append(c);
                }
            }
            // ignora outros caracteres que nao sejam letras ou espacos
        }
        
        return encoded.toString();
    }
}