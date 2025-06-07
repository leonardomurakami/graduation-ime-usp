public class DirectedGraph {
    private MyHashTable adj;
    private SimpleList vertices; // To keep track of all vertices
    private static final int HASH_TABLE_SIZE = 997;

    public DirectedGraph() {
        this.adj = new MyHashTable(HASH_TABLE_SIZE);
        this.vertices = new SimpleList();
    }

    public void addEdge(String from, String to) {
        if (!containsVertex(from)) {
            adj.put(from, new SimpleList());
            vertices.add(from);
        }
        
        if (!containsVertex(to)) {
            adj.put(to, new SimpleList());
            vertices.add(to);
        }
        
        SimpleList adjacentVertices = getAdj(from);
        adjacentVertices.add(to);
    }

    public SimpleList getAdj(String v) {
        return (SimpleList) adj.get(v);
    }

    public boolean containsVertex(String v) {
        return adj.contains(v);
    }
    
    public SimpleList getVertices() {
        return vertices;
    }

    // [debug] imprime o grafo representado como listas de adjacencia
    public void printGraph() {
        System.out.println("\nGraph representation (adjacency lists):");
        vertices.forEach(vertex -> {
            System.out.print(vertex + " -> ");
            SimpleList neighbors = getAdj(vertex);
            if (neighbors != null) {
                neighbors.forEach(neighbor -> System.out.print(neighbor + " "));
            }
            System.out.println();
        });
        System.out.println();
    }
}