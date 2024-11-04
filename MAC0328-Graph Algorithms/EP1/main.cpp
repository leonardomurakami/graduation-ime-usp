#include <boost/config.hpp>
#include <iostream>
#include <vector>
#include <boost/graph/strong_components.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/topological_sort.hpp>
#include <boost/foreach.hpp>

typedef std::pair<int, int> C;
typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::directedS> Graph;
typedef boost::graph_traits<Graph>::vertex_descriptor Vertex;

int variable_to_vertex(int var, int n)
{
    if(var < 0)
        return (-var + n - 1);
    else
        return var - 1;
}

int main(int argc, char ** argv)
{
    int DEBUG_LEVEL, n, m, x, y;
    std::cin >> DEBUG_LEVEL;
    std::cin >> n >> m;
    std::vector<C> Cs;
    

    for (int i=0; i < m; i++){
      std::cin >> x >> y;
      Cs.push_back(C(x, y));  
    }
    if(DEBUG_LEVEL == 2){
      std::cout << n << " " << m*2 << std::endl;
    }
    Graph g(n*2);
    //digraph creation based on clauses
    BOOST_FOREACH(C c, Cs)
    {
        int v1 = c.first;
        int v2 = c.second;
        boost::add_edge(
                variable_to_vertex(-v1, n),
                variable_to_vertex(v2, n),
                g);
        boost::add_edge(
                variable_to_vertex(-v2, n),
                variable_to_vertex(v1, n),
                g);
        if(DEBUG_LEVEL == 2){
          std::cout << -v1 << " " << v2 << std::endl;
          std::cout << -v2 << " " << v1 << std::endl;
        }
    }
    //utilize native boost function to find reverse topologically ordered strongly connected components
    std::vector<int> component(num_vertices(g));
    std::vector<int> solution(n); 
    strong_components(
      g, 
      make_iterator_property_map(component.begin(), get(boost::vertex_index, g))
    );

    bool satisfied = true;
    //if x and ~x are in the same scc, this means they can both reach each other,
    //this would imply that x -> ~x (x implies ~x) and ~x -> x (~x implies x)
    //which is absurd
    
    //at the same time, since the sccs are reverse topologically ordered, if the
    //component associated with lit is before (in order) than ~lit this
    //shows that it is possible to reach ~lit from lit, meaning it should be true (otherwise false)
    if(DEBUG_LEVEL == 0){
      for(int i=0; i<n; i++)
      {
        if(component[i] == component[i+n]){       
          satisfied = false;
        }
        if(component[i] < component[i+n]){
          solution[i] = 1;
        } else if (component[i] > component[i+n]) {
          solution[i] = 0;
        }
      }

      if(satisfied){
        std::cout << "YES ";
        for (int i=0; i<n; i++){
          std::cout << solution[i] << " ";
        }
        std::cout << std::endl;
      }
      else
        std::cout << "NO" << std::endl;
    }
    else if(DEBUG_LEVEL == 1){
      for(int i = 0; i<n*2; i++){
        std::cout << component[i]+1 << " ";
      }
      std::cout << std::endl;
    }
}