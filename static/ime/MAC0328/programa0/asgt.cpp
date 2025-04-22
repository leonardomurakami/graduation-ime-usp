/* This is the main file that the students must work on to submit; the
 * other one is arb.h
 */

#include "asgt.h"
Arb read_arb(std::istream &in)
{
  int num_vertex;
  in >> num_vertex;
  
  Arb arb(num_vertex);
  int x, y;
  for(int i = 1; i < num_vertex; i++){
    std::cin >> x >> y;
    boost::add_edge(--x, --y, arb);
  }
  return arb;
}

void dfs(Arb &arb, const Vertex& u, const Vertex& parent, HeadStart& data, long int& time)
{
    data.insertDiscoverTime(u, time++);
    for (auto vd : boost::make_iterator_range(adjacent_vertices(u, arb))) {
        if (vd != parent)
            dfs(arb, vd, u, data, time);
    }
    data.insertExitTime(u, time++);
}

void non_recursive_dfs(Arb &arb, const Vertex& u, const Vertex& parent, HeadStart& data, long int& time)
{
    data.insertDiscoverTime(u, time++);
    
    for (auto vd : boost::make_iterator_range(adjacent_vertices(u, arb))) {
        if (vd != parent)
            dfs(arb, vd, u, data, time);
    }
    data.insertExitTime(u, time++);
}

HeadStart preprocess(Arb &arb, const Vertex& root)
{
  HeadStart h = HeadStart(10000000);
  long int time = 0;
  dfs(arb, root, -1, h, time);
  return h;
}

bool is_ancestor (const Vertex& u, const Vertex& v, const HeadStart& data)
{
  bool b = (data.getDiscoverTime(u) <= data.getDiscoverTime(v) &&
             data.getExitTime(v) <= data.getExitTime(u));
  return b;
}
