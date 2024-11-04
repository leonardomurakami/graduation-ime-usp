#ifndef GRAPH_H
#define GRAPH_H

#define BOOST_ALLOW_DEPRECATED_HEADERS // silence warnings
#include <boost/graph/graph_traits.hpp>
#include <boost/graph/adjacency_list.hpp>

/* Students may add any number of fields and methods to this struct;
 * however the cutvertex field must be preserved unchanged, and it
 * must be filled with the appropriate boolean value according to the
 * debug level. */
struct BundledVertex {
  bool cutvertex;               // if it is a cut vertice
  bool visited = false;         // visited by dfs
  int disc = 0;                 // discovery time
  int low = INT_MAX;            // topmost reachable ancestor
  int parent = -1;              // node parent invoked by dfs
};

/* Students may add any number of fields and methods to this struct;
 * however the bcc and bridge fields must be preserved unchanged, and
 * they must be filled with the appropriate values according to the
 * debug level. */
struct BundledEdge {
  size_t bcc;                   // biconnected component label
  bool bridge;                  // if it is a bridge
};

/* the remainder of the file must not be changed */
typedef boost::adjacency_list<boost::vecS,
                              boost::vecS,
                              boost::undirectedS,
                              BundledVertex,
                              BundledEdge> Graph;
typedef boost::graph_traits<Graph>::vertex_descriptor Vertex;
typedef boost::graph_traits<Graph>::edge_descriptor Edge;

#endif // #ifndef GRAPH_H
