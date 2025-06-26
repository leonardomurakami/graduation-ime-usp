import java.io.File;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Represents a node in the Huffman tree.
 * Can be either an internal node or a leaf node.
 * Implements Comparable to be used in a PriorityQueue.
 */
class HuffmanNode implements Comparable<HuffmanNode> {
    final String symbol;      // The symbol for a leaf node
    final int frequency;    // Frequency of the symbol or sum of frequencies of children
    final HuffmanNode left;   // Left child
    final HuffmanNode right;  // Right child

    HuffmanNode(String symbol, int frequency, HuffmanNode left, HuffmanNode right) {
        this.symbol = symbol;
        this.frequency = frequency;
        this.left = left;
        this.right = right;
    }

    /**
     * Checks if the node is a leaf node.
     * @return true if it's a leaf, false otherwise.
     */
    boolean isLeaf() {
        return this.left == null && this.right == null;
    }

    /**
     * Compares nodes based on their frequency.
     * @param other The node to compare to.
     * @return a negative integer, zero, or a positive integer as this node's
     *         frequency is less than, equal to, or greater than the other node's frequency.
     */
    @Override
    public int compareTo(HuffmanNode other) {
        return this.frequency - other.frequency;
    }
}

/**
 * Implements the second program of the series, which builds a Huffman tree
 * from a given text and serializes it.
 */
public class Programa2 {

    /**
     * Main method. Reads a file, builds a Huffman tree, and prints the serialized tree.
     * @param args Command line arguments, expects one argument: the input file path.
     */
    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Usage: java Programa2 <input_file>");
            System.exit(1);
        }

        String inputFilePath = args[0];
        String text = "";

        try (Scanner scanner = new Scanner(new File(inputFilePath))) {
            if (scanner.hasNextLine()) {
                text = scanner.nextLine();
            }
        } catch (FileNotFoundException e) {
            System.err.println("Error: Input file not found: " + inputFilePath);
            System.exit(1);
        }

        Map<String, Integer> frequencies = calculateFrequencies(text);

        if (frequencies.isEmpty()) {
            return; 
        }

        HuffmanNode root = buildHuffmanTree(frequencies);
        
        StringBuilder serializedTree = new StringBuilder();
        serializeTree(root, serializedTree);
        
        System.out.print(serializedTree.toString());
    }

    /**
     * Calculates the frequency of each symbol in the input text.
     * A symbol is a LaTeX-like code (e.g., $\bowtie$) or a period.
     * @param text The input string.
     * @return A map from symbols to their frequencies.
     */
    private static Map<String, Integer> calculateFrequencies(String text) {
        Map<String, Integer> frequencies = new HashMap<>();
        Pattern pattern = Pattern.compile("(\\$[^$]+\\$|\\.)");
        Matcher matcher = pattern.matcher(text);

        while (matcher.find()) {
            String symbol = matcher.group(1);
            frequencies.put(symbol, frequencies.getOrDefault(symbol, 0) + 1);
        }
        return frequencies;
    }

    /**
     * Builds the Huffman tree from the symbol frequencies.
     * @param frequencies A map of symbols to their frequencies.
     * @return The root node of the Huffman tree.
     */
    private static HuffmanNode buildHuffmanTree(Map<String, Integer> frequencies) {
        PriorityQueue<HuffmanNode> pq = new PriorityQueue<>();

        for (Map.Entry<String, Integer> entry : frequencies.entrySet()) {
            pq.add(new HuffmanNode(entry.getKey(), entry.getValue(), null, null));
        }

        if (pq.size() == 1) {
            HuffmanNode leaf = pq.poll();
            return new HuffmanNode(null, leaf.frequency, leaf, null);
        }
        
        while (pq.size() > 1) {
            HuffmanNode left = pq.poll();
            HuffmanNode right = pq.poll();

            int sumFrequency = left.frequency + right.frequency;
            HuffmanNode parent = new HuffmanNode(null, sumFrequency, left, right);
            pq.add(parent);
        }

        return pq.poll();
    }

    /**
     * Serializes the Huffman tree using a pre-order traversal.
     * Internal nodes are represented by '0'.
     * Leaf nodes are represented by '1' followed by the symbol.
     * @param node The current node to serialize.
     * @param sb The StringBuilder to append the serialized string to.
     */
    private static void serializeTree(HuffmanNode node, StringBuilder sb) {
        if (node == null) {
            return;
        }

        if (node.isLeaf()) {
            sb.append('1');
            sb.append(node.symbol);
        } else {
            sb.append('0');
            serializeTree(node.left, sb);
            serializeTree(node.right, sb);
        }
    }
}
