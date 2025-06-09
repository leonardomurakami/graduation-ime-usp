public class CycleDetector {
    private DirectedGraph graph;
    private MyHashTable visited;
    private MyHashTable onStack;
    private boolean hasCycle;
    private static final int HASH_TABLE_SIZE = 997;
    public CycleDetector(DirectedGraph graph) {
        this.graph = graph;
        this.visited = new MyHashTable(HASH_TABLE_SIZE);
        this.onStack = new MyHashTable(HASH_TABLE_SIZE);
        this.hasCycle = false;
    }

    public boolean hasCycle() {
        SimpleList vertices = graph.getVertices();
        
        vertices.forEach(vertex -> {
            if (!visited.contains(vertex)) {
                dfs(vertex);
            }
        });
        
        return hasCycle;
    }
    
    private void dfs(String v) {
        visited.put(v, true);
        onStack.put(v, true);
        
        SimpleList adjacentVertices = graph.getAdj(v);
        if (adjacentVertices != null) {
            adjacentVertices.forEach(neighbor -> {
                if (hasCycle) return;
                
                if (!visited.contains(neighbor)) {
                    dfs(neighbor);
                } 
                else if (onStack.contains(neighbor)) {
                    hasCycle = true;
                }
            });
        }
        
        onStack.put(v, false);
    }
}