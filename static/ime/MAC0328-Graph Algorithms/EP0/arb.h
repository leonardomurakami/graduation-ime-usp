/* the definition of HeadStart may be changed in this file; the rest
 * MUST NOT be changed
 */

#ifndef ARB_H
#define ARB_H

#define BOOST_ALLOW_DEPRECATED_HEADERS // silence warnings
#include <boost/graph/graph_traits.hpp>
#include <boost/graph/adjacency_list.hpp>

typedef boost::adjacency_list<boost::vecS,
                              boost::vecS,
                              boost::directedS> Arb;
typedef boost::graph_traits<Arb>::vertex_descriptor Vertex;

/* Students must adapt this class for their needs; the innards of
   these objects are only accessed by the student's code */

class HeadStart {

  public:
    HeadStart(int nodes): exitTime(nodes), discoverTime(nodes) {};

    void insertExitTime(int node, int value){
      exitTime[node] = value;
    };
    void insertDiscoverTime(int node, int value){
      discoverTime[node] = value;
    };
    
    int getExitTime(const Vertex& u) const{
      return exitTime[u];
    };
    int getDiscoverTime(const Vertex& u) const{
      return discoverTime[u];
    };


  private:
    std::vector<int> exitTime;
    std::vector<int> discoverTime;
};

#endif // #ifndef ARB_H
