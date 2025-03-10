#include <iostream>

#define BOOST_ALLOW_DEPRECATED_HEADERS
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graph_traits.hpp>
#include <boost/graph/graphviz.hpp>

/* Students may add any number of fields and methods to this struct */
struct BundledVertex{
  bool visited;
};

struct BundledArc{
  int maxCapacity;
  int currentCapacity;
  int vector_position;
  bool reversed;
};

typedef boost::adjacency_list<
  boost::vecS,
  boost::vecS,
  boost::directedS,
  BundledVertex,
  BundledArc
> Digraph;

typedef boost::graph_traits<Digraph>::edge_descriptor Arc;
typedef boost::graph_traits<Digraph>::vertex_descriptor Vertex;

template <typename T>
void print_vector(std::vector<T> v){
  std::cout << "[";
  for(auto vi : v){
    std::cout << vi << ", ";
  }
  std::cout << "]" << std::endl;
}

int main() {
  int                                         num_vertexes, num_arcs  ;
  int                                         maxFlow = 0             ;
  int                                         u, v, capacity          ;
  int                                         vector_size = 0         ;
  unsigned int                                source, sink            ;
  std::vector<Arc>                            arcs_order              ;
  std::vector<Arc>                            reversed_arcs_order     ;
  Arc                                         aux                     ; 
  Arc                                         aux_rev                 ;

  std::cin >> num_vertexes >> num_arcs;
  std::cin >> source >> sink;
  source--;
  sink--;
  
  Digraph                                     digraph(num_vertexes)   ;
  for(int i=0; i<num_arcs; i++){
    std::cin >> u >> v >> capacity;
    // create directed edge
    std::tie(aux, std::ignore) = boost::add_edge(u-1, v-1, digraph);
    digraph[aux].maxCapacity = capacity;
    digraph[aux].currentCapacity = capacity;
    digraph[aux].vector_position = vector_size;
    digraph[aux].reversed = false;
    arcs_order.push_back(aux);
    // create reversed edge
    std::tie(aux_rev, std::ignore) = boost::add_edge(v-1, u-1, digraph);
    digraph[aux_rev].maxCapacity = capacity;
    digraph[aux_rev].currentCapacity = 0;
    digraph[aux_rev].vector_position = vector_size;
    digraph[aux_rev].reversed = true;
    reversed_arcs_order.push_back(aux_rev);
    vector_size += 1;
  }
  //create digraph
  //store arcs in vector and in digraph
  while(true){
    int                                       bottleneck              ;
    Arc                                       edge, reversed_edge     ;
    Vertex                                    node                    ;
    std::list<int>                            pathBottleneckQueue     ;
    std::vector<unsigned int>                 reachableFromSource     ;
    std::vector<Arc>                          path                    ;
    std::list<std::vector<Arc>>               queue                   ;


    //since we are able to have multiple arcs from vertex A to vertex B
    //due to the occurence of edge (A, B) and edge (B, A) through reversal
    //we are going to traverse the BFS and keep track of the augmenting path
    //through Arcs. Since Arcs have pointers that store the correct data
    //we wont be risking running into an ocasion where there is an Arc from
    //A to B and a reverse Arc (in the residual Digraph) from A to B and getting
    //the wrong Arc from the boost::edge function
    pathBottleneckQueue.clear();
    queue.clear();

    path = std::vector<Arc>();

    reachableFromSource = {source};
    bottleneck = INT_MAX;
    node = source;
    //////////////////////////// BFS STARTUP //////////////////////////////////
    for(int i=0; i<num_vertexes; i++){
      digraph[i].visited = false;
    }
    digraph[source].visited = true;
    //////////////////////////// BFS STARTUP //////////////////////////////////
    //////////////////////////// EPOCH PRINTOUTS //////////////////////////////
    for(unsigned int i=0; i < arcs_order.size(); i++){
      std::cout << digraph[arcs_order[i]].currentCapacity << " " << digraph[reversed_arcs_order[i]].currentCapacity << std::endl;
    }
    //////////////////////////// EPOCH PRINTOUTS //////////////////////////////
    //////////////////////////////// START BFS ////////////////////////////////
    while(true){
      if (node == sink){
        break;
      }
      typename boost::graph_traits<Digraph>::out_edge_iterator ei, ei_end;
      for (boost::tie(ei, ei_end) = out_edges(node, digraph); ei != ei_end; ei++) {
        if(
          digraph[*ei].currentCapacity > 0 and 
          !digraph[boost::target(*ei, digraph)].visited
        ){
          path.push_back(*ei); 
          queue.push_back(path);
          path.pop_back();
          digraph[boost::target(*ei, digraph)].visited = true;
          if(bottleneck > digraph[*ei].currentCapacity){
            pathBottleneckQueue.push_back(digraph[*ei].currentCapacity);
          } else {
            pathBottleneckQueue.push_back(bottleneck);
          }
        }
      }
      if (queue.empty()){
        path = std::vector<Arc>();
        bottleneck = INT_MAX;
        break;    
      }
      path = queue.front(); queue.pop_front();
      bottleneck = pathBottleneckQueue.front(); pathBottleneckQueue.pop_front();
      node = boost::target(path.back(), digraph);
      reachableFromSource.push_back(node); 
    }
    //////////////////////////////// END BFS ////////////////////////////////
    //////////////////////////// START ED-KARP //////////////////////////////
    if (path.empty()){
      std::cout << 1 << " " << maxFlow << " " << reachableFromSource.size();
      std::sort(reachableFromSource.begin(), reachableFromSource.end());
      for(unsigned int i = 0; i < reachableFromSource.size(); i++){
        std::cout << " " << reachableFromSource[i]+1;
      }
      break; 
    } 
    else { std::cout << 0 << " " << bottleneck << " " << path.size() << std::endl; }
    //do edmonds karp magic
    for(unsigned int i=0; i<path.size(); i++){
      edge = path[i];
      if(digraph[edge].reversed){
        std::cout << -(digraph[edge].vector_position+1) << " "; 
        reversed_edge = arcs_order[digraph[edge].vector_position];
      } else {
        reversed_edge = reversed_arcs_order[digraph[edge].vector_position];
        std::cout << digraph[edge].vector_position+1 << " ";
      }
      digraph[edge].currentCapacity -= bottleneck;
      digraph[reversed_edge].currentCapacity += bottleneck;
    }
    std::cout << std::endl;
    maxFlow += bottleneck;
    //////////////////////////// END ED-KARP //////////////////////////////
  }
} 