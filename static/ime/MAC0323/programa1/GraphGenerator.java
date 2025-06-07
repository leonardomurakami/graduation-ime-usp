import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

public class GraphGenerator {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java GraphGenerator <number_of_nodes> [output_file]");
            return;
        }

        int nodes = Integer.parseInt(args[0]);
        String outputFile = args.length > 1 ? args[1] : "random.graph";
        
        try {
            generateRandomGraph(nodes, outputFile);
            System.out.println("Random graph with " + nodes + " nodes generated in " + outputFile);
        } catch (IOException e) {
            System.err.println("Error generating graph: " + e.getMessage());
        }
    }

    private static void generateRandomGraph(int nodes, String filename) throws IOException {
        if (nodes <= 0) {
            throw new IllegalArgumentException("Number of nodes must be positive");
        }

        Random rand = new Random();
        FileWriter writer = new FileWriter(filename);

        // Generate node labels (A, B, C, ...)
        char[] nodeLabels = new char[nodes];
        for (int i = 0; i < nodes; i++) {
            nodeLabels[i] = (char) ('A' + (i % 26));
        }

        // Generate random edges
        // For simplicity, we'll generate between n and 2n edges
        int edgeCount = rand.nextInt(nodes) + nodes;
        
        for (int i = 0; i < edgeCount; i++) {
            int from = rand.nextInt(nodes);
            int to = rand.nextInt(nodes);
            
            // Avoid self-loops
            while (to == from) {
                to = rand.nextInt(nodes);
            }
            
            writer.write(nodeLabels[from] + " " + nodeLabels[to] + "\n");
        }
        
        writer.close();
    }
} 