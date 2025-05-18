import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("Digite o caminho para o arquivo do grafo: ");
        String filePath = scanner.nextLine();
        
        DirectedGraph graph = readGraphFromFile(filePath);
        
        if (graph != null) {
            CycleDetector cycleDetector = new CycleDetector(graph);
            boolean hasCycle = cycleDetector.hasCycle();
            
            if (hasCycle) {
                System.out.println("O grafo contem ciclos.");
            } else {
                System.out.println("O grafo nao contem ciclos.");
            }
            
            // Find paths between two vertices
            System.out.print("Digite o vertice de origem: ");
            String source = scanner.nextLine();
            
            System.out.print("Digite o vertice de destino: ");
            String target = scanner.nextLine();
            
            System.out.println("Todos os caminhos de " + source + " para " + target + ":");
            PathFinder pathFinder = new PathFinder(graph);
            pathFinder.findAllPaths(source, target);
        }
        
        scanner.close();
    }
    
    private static DirectedGraph readGraphFromFile(String filePath) {
        DirectedGraph graph = new DirectedGraph();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] vertices = line.trim().split("\s+");
                if (vertices.length >= 2) {
                    String from = vertices[0];
                    String to = vertices[1];
                    graph.addEdge(from, to);
                }
            }
            System.out.println("Grafo carregado com sucesso.");
            return graph;
        } catch (IOException e) {
            System.out.println("Erro ao ler o arquivo do grafo: " + e.getMessage());
            return null;
        }
    }
}