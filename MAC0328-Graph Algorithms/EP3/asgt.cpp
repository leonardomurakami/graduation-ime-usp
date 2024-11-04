#include "asgt.h"

#include <utility>              // for std::get
#include <tuple>
#include <vector>
#include <math.h> 
#include <algorithm>

#define BOOST_ALLOW_DEPRECATED_HEADERS // silence warnings
#include <boost/graph/adjacency_list.hpp>
#include <boost/optional.hpp>

#include "cycle.h"
#include "digraph.h"
#include "potential.h"

/* The code in this template file is all "bogus". It just illustrates
 * how to return answers back to main.cpp. */

/* The following declarations shorten the bogus code below. Feel free
 * to change/drop them. */
using boost::add_edge;
using boost::num_vertices;
using boost::out_edges;
using std::vector;
using std::cout;
using std::endl;


void print_vector(std::vector<unsigned int> v){
  cout << "[";
  for(auto vi : v){
    cout << vi << ", ";
  }
  cout << "]" << endl;
}

Digraph build_digraph(const Digraph& market)
{
  Digraph digraph(num_vertices(market));
  Arc aux;
  auto es = boost::edges(market);
  for (auto eit = es.first; eit != es.second; ++eit) {
      Vertex u = boost::source(*eit, market);
      Vertex v = boost::target(*eit, market);
      aux = add_edge(u,v,digraph).first;
      //store as negative log so:
      // values that are between 0 and 1 become positive
      // and values that are above 1 become negative
      // so if we search for negative cycles, it should yield a positive
      // multiplication
      digraph[aux].cost = -log(market[*eit].cost);
      digraph[v].parent_vertexes.push_back(u);
   }
  return digraph;
}

std::tuple<unsigned int, std::vector<double>> bellman_ford(Digraph& digraph, unsigned int s){
  for (unsigned int i = 0; i < num_vertices(digraph); i++){
    digraph[i].dist.push_back(INT_MAX);
    digraph[i].walk.push_back({});
    digraph[i].visited.push_back(std::vector<bool>(num_vertices(digraph), false));
  }
  digraph[s].dist[0] = 0;
  digraph[s].walk[0] = {s};
  digraph[s].visited[0][0] = true;
  std::vector<double> y(num_vertices(digraph), 0);
  // for l from 1 to n
  for (unsigned int l = 1; l <= num_vertices(digraph); l++){
    // do for each vertex
    for (unsigned int v = 0; v < num_vertices(digraph); v++){
      // for each arc entering v
      digraph[v].dist.push_back(digraph[v].dist[l-1]);
      digraph[v].walk.push_back(digraph[v].walk[l-1]);
      digraph[v].visited.push_back(digraph[v].visited[l-1]);
      for (unsigned int u: digraph[v].parent_vertexes) {
        Arc eit = edge(u, v, digraph).first;
        double c_uv = digraph[eit].cost;
        
        if(y[v] >= y[u] + c_uv){
          y[v] -= (y[v] - (y[u] + c_uv));
        }
        if(digraph[v].dist[l] > digraph[u].dist[l-1] + c_uv){
          digraph[v].dist[l] = digraph[u].dist[l-1] + c_uv;
          digraph[v].walk[l] = digraph[u].walk[l-1];
          digraph[v].walk[l].push_back(v);
          digraph[v].visited[l] = digraph[u].visited[l-1];
          //if walk has already passed through v and has returned
          //we have found a negative cycle
          if (digraph[u].visited[l-1][v]){
            //while this is not a space efficient solution (since it stores n vectors of n size)
            //this could help to improve efficiency, making O(mn) the worst case cenario
            return {v, y};
          }else{
            digraph[v].visited[l][v] = true;
          }
        }
      }
    }
  }
  return {INT_MAX, y};
}

std::tuple<bool,
           boost::optional<NegativeCycle>,
           boost::optional<FeasiblePotential>>
has_negative_cycle(Digraph& digraph)
{
  std::vector<double> y;
  unsigned int cycle_start;

  std::tie(cycle_start, y) = bellman_ford(digraph, 0);
  bool negative_cycle = not(cycle_start == INT_MAX);
  
  if(negative_cycle){
    std::vector<unsigned int> cycle = digraph[cycle_start].walk.back();
    Walk walk(digraph, cycle_start);
    bool loop_start = false;
    for(std::vector<unsigned int>::size_type i = 0; i != cycle.size(); i++) {
      if(loop_start){
        walk.extend(edge(cycle[i-1], cycle[i],digraph).first);
      } else {
        if (cycle[i] == cycle_start){
          loop_start = true;
        }
      }
    }
    return{negative_cycle, NegativeCycle(walk), boost::none};
  }
  return {negative_cycle, boost::none, FeasiblePotential(digraph, y)};
}

Loophole build_loophole(const NegativeCycle& negcycle,
                        const Digraph& aux_digraph,
                        const Digraph& market)
{
  Walk w(market, source(negcycle.get()[0], aux_digraph));
  Arc aux;
  for (auto &arc : negcycle.get()){  
    typename boost::graph_traits <Digraph>::out_edge_iterator ei, ei_end;
    std::tie(aux, std::ignore) = edge(source(arc, aux_digraph), target(arc, aux_digraph), market);
    w.extend(aux);
  }
  return Loophole(w);
}

FeasibleMultiplier build_feasmult(const FeasiblePotential& feaspot,
                                  const Digraph& aux_digraph,
                                  const Digraph& market)
{
  vector<double> z(num_vertices(aux_digraph), 0);
  vector<double> y;
  y = feaspot.potential();
  for(unsigned int i=0; i<num_vertices(aux_digraph);i++){
    z[i] = exp(-y[i]);
  }
  return FeasibleMultiplier(market, z);
}
