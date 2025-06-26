import networkx as nx
import numpy as np
from collections import defaultdict

class FloydWarshall:
    def __init__(self, graph):
        """
        Initialize Floyd-Warshall algorithm with a NetworkX graph
        
        Args:
            graph: NetworkX graph (can be directed or undirected)
        """
        self.graph = graph
        self.nodes = list(graph.nodes())
        self.n = len(self.nodes)
        self.node_to_index = {node: i for i, node in enumerate(self.nodes)}
        self.index_to_node = {i: node for i, node in enumerate(self.nodes)}
        
        # Initialize distance and predecessor matrices
        self.dist = np.full((self.n, self.n), float('inf'))
        self.pred = np.full((self.n, self.n), -1, dtype=int)
        
        # Initialize distance matrix
        self._initialize_distances()
        
    def _initialize_distances(self):
        """Initialize distance matrix with edge weights and diagonal zeros"""
        # Distance from a node to itself is 0
        for i in range(self.n):
            self.dist[i][i] = 0
            
        # Set distances for existing edges
        for u, v, data in self.graph.edges(data=True):
            u_idx = self.node_to_index[u]
            v_idx = self.node_to_index[v]
            weight = data.get('weight', 1)  # Default weight is 1
            
            self.dist[u_idx][v_idx] = weight
            self.pred[u_idx][v_idx] = u_idx
            
            # If undirected graph, add reverse edge
            if not self.graph.is_directed():
                self.dist[v_idx][u_idx] = weight
                self.pred[v_idx][u_idx] = v_idx
    
    def run_algorithm(self):
        """Execute Floyd-Warshall algorithm"""
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.pred[i][j] = self.pred[k][j]
    
    def get_path(self, start, end):
        """
        Reconstruct the shortest path between two nodes
        
        Args:
            start: Starting node
            end: Ending node
            
        Returns:
            List of nodes representing the shortest path, or None if no path exists
        """
        if start not in self.node_to_index or end not in self.node_to_index:
            return None
            
        start_idx = self.node_to_index[start]
        end_idx = self.node_to_index[end]
        
        if self.dist[start_idx][end_idx] == float('inf'):
            return None  # No path exists
        
        path = []
        current = end_idx
        
        while current != -1:
            path.append(self.index_to_node[current])
            if current == start_idx:
                break
            current = self.pred[start_idx][current]
        
        path.reverse()
        return path
    
    def get_all_paths(self):
        """
        Get all shortest paths between all pairs of vertices
        
        Returns:
            Dictionary with paths information
        """
        all_paths = {}
        
        for i, start in enumerate(self.nodes):
            all_paths[start] = {}
            for j, end in enumerate(self.nodes):
                if i != j:  # Skip same node
                    path = self.get_path(start, end)
                    distance = self.dist[i][j] if self.dist[i][j] != float('inf') else None
                    all_paths[start][end] = {
                        'path': path,
                        'distance': distance
                    }
        
        return all_paths
    
    def display_distance_matrix(self):
        """Display the distance matrix"""
        print("\nDistance Matrix:")
        print("=" * 50)
        
        # Header
        print(f"{'':>8}", end="")
        for node in self.nodes:
            print(f"{str(node):>8}", end="")
        print()
        
        # Rows
        for i, node in enumerate(self.nodes):
            print(f"{str(node):>8}", end="")
            for j in range(self.n):
                dist_val = self.dist[i][j]
                if dist_val == float('inf'):
                    print(f"{'∞':>8}", end="")
                else:
                    print(f"{dist_val:>8.1f}", end="")
            print()
    
    def display_all_paths(self):
        """Display all shortest paths between vertices"""
        print("\nAll Shortest Paths:")
        print("=" * 50)
        
        all_paths = self.get_all_paths()
        
        for start in self.nodes:
            for end in self.nodes:
                if start != end:
                    path_info = all_paths[start][end]
                    path = path_info['path']
                    distance = path_info['distance']
                    
                    if path is not None:
                        path_str = " → ".join(map(str, path))
                        print(f"{start} to {end}: {path_str} (distance: {distance})")
                    else:
                        print(f"{start} to {end}: No path exists")


def create_sample_graph():
    """Create a sample weighted graph for demonstration"""
    G = nx.DiGraph()  # You can change to nx.Graph() for undirected
    
    # Add edges with weights
    edges = [
        ('A', 'B', 3),
        ('A', 'C', 8),
        ('A', 'E', -4),
        ('B', 'D', 1),
        ('B', 'E', 7),
        ('C', 'B', 4),
        ('D', 'A', 2),
        ('D', 'C', -5),
        ('E', 'D', 6)
    ]
    
    for u, v, weight in edges:
        G.add_edge(u, v, weight=weight)
    
    return G


def main():
    """Main function to demonstrate Floyd-Warshall algorithm"""
    print("Floyd-Warshall Algorithm with NetworkX")
    print("=" * 50)
    
    # Create sample graph
    G = create_sample_graph()
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    print(f"Nodes: {list(G.nodes())}")
    print(f"Edges: {list(G.edges(data=True))}")
    
    # Initialize and run Floyd-Warshall
    fw = FloydWarshall(G)
    fw.run_algorithm()
    
    # Display results
    fw.display_distance_matrix()
    fw.display_all_paths()
    
    # Example: Get specific path
    print(f"\nSpecific path from A to C: {fw.get_path('A', 'C')}")
    
    # Create an undirected graph example
    print("\n" + "=" * 70)
    print("UNDIRECTED GRAPH EXAMPLE")
    print("=" * 70)
    
    G_undirected = nx.Graph()
    undirected_edges = [
        ('1', '2', 4),
        ('1', '3', 2),
        ('2', '3', 1),
        ('2', '4', 5),
        ('3', '4', 8),
        ('3', '5', 10),
        ('4', '5', 2)
    ]
    
    for u, v, weight in undirected_edges:
        G_undirected.add_edge(u, v, weight=weight)
    
    print(f"Undirected graph has {G_undirected.number_of_nodes()} nodes and {G_undirected.number_of_edges()} edges")
    
    fw_undirected = FloydWarshall(G_undirected)
    fw_undirected.run_algorithm()
    
    fw_undirected.display_distance_matrix()
    fw_undirected.display_all_paths()


if __name__ == "__main__":
    main()
