public class PathFinder {
    private DirectedGraph graph;
    private MyHashTable visited;
    private String[] currentPath;
    private int pathLength;
    private static final int MAX_PATH_LENGTH = 1000; // Assuming a max path length
    private static final int HASH_TABLE_SIZE = 997;
    
    public PathFinder(DirectedGraph graph) {
        this.graph = graph;
        this.currentPath = new String[MAX_PATH_LENGTH];
        this.pathLength = 0;
    }

    public void findAllPaths(String source, String target) {
        this.visited = new MyHashTable(HASH_TABLE_SIZE);
        this.pathLength = 0;
        
        if (!graph.containsVertex(source) || !graph.containsVertex(target)) {
            System.out.println("Source or target vertex does not exist in the graph.");
            return;
        }
        
        visited.put(source, true);
        dfs(source, target);
        visited.put(source, false);
    }
    
    private void dfs(String current, String target) {
        currentPath[pathLength++] = current;
        
        // // Debug print - show current exploration path
        // // AI Generated Debug Print
        // System.out.print("Exploring path: ");
        // for (int i = 0; i < pathLength; i++) {
        //     System.out.print(currentPath[i]);
        //     if (i < pathLength - 1) System.out.print(" -> ");
        // }
        // System.out.println();
        

        // se o vertice atual eh o target, imprime o caminho
        if (current.equals(target)) {
            printPath();
        }
        
        // explora todos os vertices adjacentes
        SimpleList adjacentVertices = graph.getAdj(current);
        if (adjacentVertices != null) {
            String[] neighbors = adjacentVertices.getValues();
            for (String neighbor : neighbors) {
                // verifica se o vertice vizinho esta sendo visitado nesse caminho
                Object visitedState = visited.get(neighbor);
                boolean isCurrentlyVisited = visitedState != null && visitedState instanceof Boolean && (Boolean) visitedState;
                
                if (!isCurrentlyVisited) {
                    // marca o vertice como visitado para nao entrar em loop devido a ciclos
                    visited.put(neighbor, true);
                    dfs(neighbor, target);
                    // quando der backtracking, remove o vertice da tabela de visitados
                    // para que ele possa ser visitado novamente por outro possivel caminho
                    visited.put(neighbor, false);
                }
            }
        }
        
        pathLength--;
    }
    
    private void printPath() {
        StringBuilder path = new StringBuilder();
        for (int i = 0; i < pathLength; i++) {
            path.append(currentPath[i]);
            if (i < pathLength - 1) {
                path.append(" -> ");
            }
        }
        System.out.println(path.toString());
    }
}