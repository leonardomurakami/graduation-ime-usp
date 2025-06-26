import java.io.*;
import java.util.*;

public class Programa1 {
    
    // Tabela de símbolos (inicializada vazia)
    private static Map<Character, String> symbolTable = new HashMap<>();
    
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Uso: java Programa1 <arquivo_tabela_simbolos.txt> <arquivo_entrada.txt>");
            return;
        }
        
        String symbolTableFile = args[0];
        String inputFile = args[1];
        
        // Carrega tabela de símbolos (obrigatório)
        loadSymbolTable(symbolTableFile);
        
        try {
            String inputText = readFile(inputFile);
            String encodedText = encodeText(inputText);
            System.out.println(encodedText);
        } catch (IOException e) {
            System.err.println("Erro ao ler arquivo: " + e.getMessage());
        }
    }
    
    /**
     * Lê o conteúdo de um arquivo e retorna como string
     */
    private static String readFile(String filename) throws IOException {
        StringBuilder content = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line);
                content.append(" "); // Adiciona espaço entre linhas
            }
        }
        return content.toString().trim();
    }
    
    /**
     * Carrega tabela de símbolos de um arquivo
     * Formato esperado: cada linha deve ter "letra espaço codigo_latex"
     */
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
    
    /**
     * Codifica o texto usando a tabela de símbolos
     * Espaços são convertidos para pontos
     */
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
                    // Se não encontrar símbolo, mantém o caractere original
                    encoded.append(c);
                }
            }
            // Ignora outros caracteres que não sejam letras ou espaços
        }
        
        return encoded.toString();
    }
    
    /**
     * Método auxiliar para imprimir a tabela de símbolos atual
     */
    public static void printSymbolTable() {
        System.out.println("Tabela de Símbolos:");
        for (char c = 'a'; c <= 'z'; c++) {
            String symbol = symbolTable.get(c);
            if (symbol != null) {
                System.out.println(c + " -> " + symbol);
            }
        }
    }
}