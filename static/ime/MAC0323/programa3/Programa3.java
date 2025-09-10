import java.io.*;
import java.util.*;
import javax.swing.*;
import java.awt.Color;
import java.awt.FontMetrics;
import java.awt.Graphics;

public class Programa3 {
    static class Node {
        String symbol;
        int freq;
        Node left;
        Node right;
        
        public Node(String symbol, int freq, Node left, Node right) {
            this.symbol = symbol;
            this.freq = freq;
            this.left = left;
            this.right = right;
        }
    }
    
    private static int pos = 0;
    
    private static Node readTree(String treeString) {
        if (pos >= treeString.length()) {
            return null;
        }
        
        if (treeString.charAt(pos) == '1') {
            pos++; // pula o '1'
            
            // le o simbolo ate encontrar o proximo '1' ou '0' ou fim da string
            StringBuilder symbol = new StringBuilder();
            while (pos < treeString.length() && 
                   treeString.charAt(pos) != '1' && 
                   treeString.charAt(pos) != '0') {
                symbol.append(treeString.charAt(pos));
                pos++;
            }
            
            return new Node(symbol.toString(), 0, null, null);
        } else if (treeString.charAt(pos) == '0') {
            pos++; // pula o '0'
            Node left = readTree(treeString);
            Node right = readTree(treeString);
            return new Node("", 0, left, right);
        }
        
        return null;
    }
    
    private static String decode(Node root, String compressed) {
        String result = "";
        int decodePos = 0;
        
        while (decodePos < compressed.length()) {
            Node x = root;
            
            while (x.left != null) { 
                if (decodePos >= compressed.length()) {
                    break;
                }
                
                if (compressed.charAt(decodePos) == '0') {
                    x = x.left;
                } else {
                    x = x.right;
                }
                decodePos++;
            }
            
            result = result + x.symbol;
        }
        
        return result.toString();
    }
    
    public static void main(String[] args) {
        boolean showVisualization = false;
        String treeFile = null;
        String compressedFile = null;
        
        // processa argumentos da linha de comando
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--viz")) {
                showVisualization = true;
            } else if (treeFile == null) {
                treeFile = args[i];
            } else if (compressedFile == null) {
                compressedFile = args[i];
            }
        }
        
        if (treeFile == null || compressedFile == null) {
            System.err.println("Uso: java Programa3 [--viz] <arquivo_arvore> <arquivo_comprimido>");
            System.exit(1);
        }
        
        try {
            // le a arvore de huffman serializada do primeiro arquivo
            Scanner treeScanner = new Scanner(new File(treeFile));
            String treeString = treeScanner.nextLine().trim();
            treeScanner.close();
            
            // le a mensagem comprimida do segundo arquivo
            Scanner compressedScanner = new Scanner(new File(compressedFile));
            String compressed = compressedScanner.nextLine().trim();
            compressedScanner.close();
            
            // reseta contador de posicao
            pos = 0;
            
            // le a arvore
            Node root = readTree(treeString);
            
            // decodifica a mensagem
            String decoded = decode(root, compressed);
            
            System.out.println(decoded);
            
            // exibe a arvore visualmente apenas se --viz for passado
            if (showVisualization && root != null) {
                SwingUtilities.invokeLater(() -> {
                    JFrame frame = new JFrame("Huffman Tree - Programa3");
                    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
                    frame.add(new TreePanel(root));
                    frame.setSize(800, 600);
                    frame.setLocationRelativeTo(null);
                    frame.setVisible(true);
                });
            }
            
        } catch (FileNotFoundException e) {
            System.err.println("Erro: Arquivo não encontrado - " + e.getMessage());
            System.err.println("Uso: java Programa3 [--viz] <arquivo_arvore> <arquivo_comprimido>");
            System.exit(1);
        } catch (Exception e) {
            System.err.println("Erro ao processar os arquivos: " + e.getMessage());
            System.exit(1);
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