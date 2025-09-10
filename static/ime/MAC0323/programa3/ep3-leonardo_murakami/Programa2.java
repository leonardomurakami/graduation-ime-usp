import java.io.*;
import java.util.*;
import javax.swing.*;
import java.awt.Color;
import java.awt.FontMetrics;
import java.awt.Graphics;

public class Programa2 {
    private static String saida = "";

    // classe node representa um no na arvore de huffman
    public static class Node {
        public String symbol;
        public int freq;
        public Node left;
        public Node right;

        public Node(String symbol, int freq) {
            this.symbol = symbol;
            this.freq = freq;
            this.left = null;
            this.right = null;
        }

        public Node(String symbol, int freq, Node left, Node right) {
            this.symbol = symbol;
            this.freq = freq;
            this.left = left;
            this.right = right;
        }
    }

    // analisa a entrada para extrair simbolos
    public static List<String> parseLatexSymbols(String input) {
        List<String> symbols = new ArrayList<>();
        int i = 0;
        while (i < input.length()) {
            if (input.charAt(i) == '$') {
                int end = input.indexOf('$', i + 1);
                if (end != -1) {
                    symbols.add(input.substring(i, end + 1));
                    i = end + 1;
                } else {
                    i++;
                }
            } else if (input.charAt(i) == '.') {
                symbols.add(".");
                i++;
            } else {
                i++;
            }
        }
        return symbols;
    }

    public static void writeTree(Node node) {
        if (node.left == null && node.right == null) {
            saida = saida + "1" + node.symbol;
            return;
        }
        saida = saida + "0";
        writeTree(node.left);
        writeTree(node.right);
    }

    // gera os codigos de huffman para cada simbolo na arvore
    public static void generateCodes(Node node, String code, Map<String, String> codes) {
        if (node == null) return;
        
        // se eh um no folha, armazena o codigo
        if (node.left == null && node.right == null) {
            codes.put(node.symbol, code.isEmpty() ? "0" : code);
            return;
        }
        
        // recursivamente gera codigos para os filhos
        generateCodes(node.left, code + "0", codes);
        generateCodes(node.right, code + "1", codes);
    }

    // codifica uma lista de simbolos usando os codigos de huffman
    public static String encodeSymbols(List<String> symbols, Map<String, String> codes) {
        StringBuilder encoded = new StringBuilder();
        for (String symbol : symbols) {
            encoded.append(codes.get(symbol));
        }
        return encoded.toString();
    }

    public static void main(String[] args) {
        boolean showVisualization = false;
        boolean outputCompressed = false;
        String filename = null;
        
        // processa argumentos da linha de comando
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--viz")) {
                showVisualization = true;
            } else if (args[i].equals("--output-compressed")) {
                outputCompressed = true;
            } else if (filename == null) {
                filename = args[i];
            }
        }
        
        if (filename == null) {
            System.err.println("Usage: java Programa2 [--viz] [--output-compressed] <filename>");
            System.exit(1);
        }
        
        String input = "";
        try {
            Scanner scanner = new Scanner(new File(filename));
            if (scanner.hasNextLine()) {
                input = scanner.nextLine();
            }
            scanner.close();
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + filename);
            System.exit(1);
        }

        // analisa a string de entrada para obter uma lista de simbolos
        List<String> symbols = parseLatexSymbols(input);

        // calcula a frequencia de cada simbolo
        Map<String, Integer> freq = new HashMap<>();
        for (String symbol : symbols) {
            freq.put(symbol, freq.getOrDefault(symbol, 0) + 1);
        }

        PriorityQueue<Node> nodes = new PriorityQueue<>((a, b) -> Integer.compare(a.freq, b.freq));
        for (Map.Entry<String, Integer> entry : freq.entrySet()) {
            nodes.add(new Node(entry.getKey(), entry.getValue()));
        }

        while (nodes.size() > 1) {
            Node left = nodes.poll();
            Node right = nodes.poll();

            Node parent = new Node("", left.freq + right.freq, left, right);
            nodes.add(parent);
        }

        // a arvore de huffman completa eh o ultimo no que restou na fila
        Node huffmanTree = nodes.poll();

        // escreve a estrutura da arvore na string de saida
        if (huffmanTree != null) {
            writeTree(huffmanTree);
        }
        
        // imprime a estrutura da arvore
        System.out.println(saida);

        // gera os codigos de huffman e codifica os simbolos
        if (huffmanTree != null) {
            Map<String, String> codes = new HashMap<>();
            generateCodes(huffmanTree, "", codes);
            
            String compressedString = encodeSymbols(symbols, codes);
            
            if (outputCompressed) {
                try {
                    PrintWriter writer = new PrintWriter(new FileWriter("compressed"));
                    writer.println(compressedString);
                    writer.close();
                } catch (IOException e) {
                    System.err.println("Error writing to file: " + e.getMessage());
                    System.exit(1);
                }
            }
        }

        // mostra visualizacao apenas se --viz for passado
        if (showVisualization && huffmanTree != null) {
            SwingUtilities.invokeLater(() -> {
                JFrame frame = new JFrame("Huffman Tree");
                frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
                frame.add(new TreePanel(huffmanTree));
                frame.setSize(800, 600);
                frame.setLocationRelativeTo(null);
                frame.setVisible(true);
            });
        }
    }

    public static class TreePanel extends JPanel {
        private final Node root;
        private static final int VERTICAL_GAP = 60;
        private static final int PADDING = 10;

        public TreePanel(Node root) {
            this.root = root;
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            if (root != null) {
                drawTree(g, getWidth() / 2, 40, root, getWidth() / 4);
            }
        }

        private void drawTree(Graphics g, int x, int y, Node node, int hGap) {
            String text;
            if (node.symbol == null || node.symbol.isEmpty()) {
                text = String.valueOf(node.freq);
            } else {
                text = "'" + node.symbol + "': " + node.freq;
            }

            FontMetrics fm = g.getFontMetrics();
            int stringWidth = fm.stringWidth(text);
            int nodeWidth = stringWidth + 2 * PADDING;
            int nodeHeight = fm.getHeight() + 2 * PADDING;

            int childY = y + VERTICAL_GAP + nodeHeight / 2;

            if (node.left != null) {
                int childX = x - hGap;
                g.setColor(Color.BLACK);
                g.drawLine(x, y, childX, childY);
                drawTree(g, childX, childY, node.left, hGap / 2);
            }

            if (node.right != null) {
                int childX = x + hGap;
                g.setColor(Color.BLACK);
                g.drawLine(x, y, childX, childY);
                drawTree(g, childX, childY, node.right, hGap / 2);
            }

            g.setColor(Color.LIGHT_GRAY);
            g.fillOval(x - nodeWidth / 2, y - nodeHeight / 2, nodeWidth, nodeHeight);
            g.setColor(Color.BLACK);
            g.drawOval(x - nodeWidth / 2, y - nodeHeight / 2, nodeWidth, nodeHeight);
            g.drawString(text, x - stringWidth / 2, y - fm.getHeight() / 2 + fm.getAscent() + PADDING);
        }
    }
}