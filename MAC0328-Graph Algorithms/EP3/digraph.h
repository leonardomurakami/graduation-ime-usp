#ifndef DIGRAPH_H
#define DIGRAPH_H

#define BOOST_ALLOW_DEPRECATED_HEADERS // silence warnings
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graph_traits.hpp>

/* Students may add any number of fields and methods to this struct */
struct BundledVertex
{
    std::vector<int> parent_vertexes;             //store vertexes source from in arc
    std::vector<std::vector<unsigned int>> walk;  //store walks
    std::vector<double> dist;                     //store "distance" from source
    std::vector<std::vector<bool>> visited;       //store if a vertex was already visited in that walk
};

/* Students may add any number of fields and methods to this struct;
 * however the cost field must be preserved unchanged, and they must
 * be filled with some cost to be used by the has_negative_cycle
 * function. */
struct BundledArc
{
  double cost;
  BundledArc() : cost(0.0) {}
};

/* the remainder of the file must not be changed */
typedef boost::adjacency_list<boost::vecS,
                              boost::vecS,
                              boost::directedS,
                              BundledVertex,
                              BundledArc> Digraph;
typedef boost::graph_traits<Digraph>::edge_descriptor Arc;
typedef boost::graph_traits<Digraph>::vertex_descriptor Vertex;

#endif // #ifndef DIGRAPH_H
