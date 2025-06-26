import java.io.*;
import java.util.*;

public class Programa3 {
    
    // Classe para representar nós da árvore de Huffman
    static class HuffmanNode {
        String symbol;
        HuffmanNode left;
        HuffmanNode right;
        
        public HuffmanNode(String symbol) {
            this.symbol = symbol;
            this.left = null;
            this.right = null;
        }
        
        public HuffmanNode() {
            this.symbol = null;
            this.left = null;
            this.right = null;
        }
        
        public boolean isLeaf() {
            return left == null && right == null;
        }
    }
    
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Uso: java Programa3 <arquivo_arvore.txt> <arquivo_codigo_binario.txt>");
            return;
        }
        
        String treeFile = args[0];
        String binaryFile = args[1];
        
        try {
            String encodedTree = readFile(treeFile).trim();
            String binaryCode = readFile(binaryFile).trim();
            
            // Reconstrói a árvore de Huffman
            HuffmanNode root = decodeTree(encodedTree);
            
            if (root != null) {
                // Decodifica a string binária
                String decodedText = decodeText(binaryCode, root);
                System.out.println(decodedText);
            } else {
                System.err.println("Erro: Não foi possível reconstruir a árvore.");
            }
            
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
            }
        }
        return content.toString();
    }
    
    /**
     * Reconstrói a árvore de Huffman a partir da string codificada
     * Formato: percurso pré-ordem onde 0=esquerda, 1=direita, folhas são inseridas diretamente
     */
    private static HuffmanNode decodeTree(String encodedTree) {
        if (encodedTree == null || encodedTree.isEmpty()) {
            return null;
        }
        
        TreeDecoderCorrect decoder = new TreeDecoderCorrect(encodedTree);
        return decoder.decode();
    }
    
    /**
     * Classe auxiliar para decodificar a árvore
     */
    private static class TreeDecoder {
        private String encoded;
        private int position;
        
        public TreeDecoder(String encoded) {
            this.encoded = encoded;
            this.position = 0;
        }
        
        public HuffmanNode decode() {
            if (position >= encoded.length()) {
                return null;
            }
            
            char current = encoded.charAt(position);
            
            // Se é um dígito (0 ou 1), é um nó interno
            if (current == '0' || current == '1') {
                position++; // Avança para o próximo caractere
                
                HuffmanNode node = new HuffmanNode();
                
                if (current == '0') {
                    // Vai para a esquerda
                    node.left = decode();
                } else {
                    // Vai para a direita
                    node.right = decode();
                }
                
                return node;
            } else {
                // É uma folha - extrai o símbolo
                String symbol = extractSymbol();
                return new HuffmanNode(symbol);
            }
        }
        
        private String extractSymbol() {
            if (position >= encoded.length()) {
                return "";
            }
            
            // Se começa com $, é um código LaTeX
            if (encoded.charAt(position) == '$') {
                int start = position;
                position++; // Pula o primeiro $
                
                // Encontra o $ de fechamento
                while (position < encoded.length() && encoded.charAt(position) != '$') {
                    position++;
                }
                
                if (position < encoded.length()) {
                    position++; // Pula o $ de fechamento
                    return encoded.substring(start, position);
                } else {
                    // Erro: $ não fechado
                    return encoded.substring(start);
                }
            } else {
                // É um ponto ou outro caractere simples
                char symbol = encoded.charAt(position);
                position++;
                return String.valueOf(symbol);
            }
        }
    }
    
    /**
     * Reconstrói a árvore de Huffman corretamente
     */
    private static HuffmanNode decodeTreeCorrect(String encodedTree) {
        if (encodedTree == null || encodedTree.isEmpty()) {
            return null;
        }
        
        TreeDecoderCorrect decoder = new TreeDecoderCorrect(encodedTree);
        return decoder.decode();
    }
    
    private static class TreeDecoderCorrect {
        private String encoded;
        private int position;
        
        public TreeDecoderCorrect(String encoded) {
            this.encoded = encoded;
            this.position = 0;
        }
        
        public HuffmanNode decode() {
            if (position >= encoded.length()) {
                return null;
            }
            
            char current = encoded.charAt(position);
            
            // Se não é um dígito (0 ou 1), é uma folha
            if (current != '0' && current != '1') {
                String symbol = extractSymbol();
                return new HuffmanNode(symbol);
            }
            
            // É um nó interno
            HuffmanNode node = new HuffmanNode();
            
            // Processa todos os filhos sequencialmente
            while (position < encoded.length() && (encoded.charAt(position) == '0' || encoded.charAt(position) == '1')) {
                char direction = encoded.charAt(position);
                position++; // Consome o dígito de direção
                
                HuffmanNode child = decode();
                
                if (direction == '0') {
                    node.left = child;
                } else { // direction == '1'
                    node.right = child;
                }
            }
            
            return node;
        }
        
        private String extractSymbol() {
            if (position >= encoded.length()) {
                return "";
            }
            
            // Se começa com $, é um código LaTeX
            if (encoded.charAt(position) == '$') {
                int start = position;
                position++; // Pula o primeiro $
                
                // Encontra o $ de fechamento
                while (position < encoded.length() && encoded.charAt(position) != '$') {
                    position++;
                }
                
                if (position < encoded.length()) {
                    position++; // Pula o $ de fechamento
                    return encoded.substring(start, position);
                } else {
                    // Erro: $ não fechado
                    return encoded.substring(start);
                }
            } else {
                // É um ponto ou outro caractere simples
                char symbol = encoded.charAt(position);
                position++;
                return String.valueOf(symbol);
            }
        }
    }
    
    /**
     * Decodifica o texto binário usando a árvore de Huffman
     */
    private static String decodeText(String binaryCode, HuffmanNode root) {
        if (binaryCode == null || binaryCode.isEmpty() || root == null) {
            return "";
        }
        
        StringBuilder decoded = new StringBuilder();
        HuffmanNode current = root;
        
        for (char bit : binaryCode.toCharArray()) {
            if (bit == '0') {
                current = current.left;
            } else if (bit == '1') {
                current = current.right;
            } else {
                // Ignora caracteres que não são 0 ou 1
                continue;
            }
            
            // Se chegou a uma folha, adiciona o símbolo e volta para a raiz
            if (current != null && current.isLeaf()) {
                decoded.append(current.symbol);
                current = root;
            } else if (current == null) {
                // Erro: caminho inválido na árvore
                System.err.println("Erro: Caminho inválido na decodificação.");
                break;
            }
        }
        
        return decoded.toString();
    }
} 