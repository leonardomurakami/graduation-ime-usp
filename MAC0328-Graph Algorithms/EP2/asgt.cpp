#include <iostream>
#include "asgt.h"

void dfs_fill(Graph &g, const Vertex& v, const Vertex& parent, long int& time)
{

    time++;
    g[v].visited = true;
    g[v].disc = g[v].low = time+1;
    int children = 0;
    for (auto vd : boost::make_iterator_range(adjacent_vertices(v, g))) {
        if (g[vd].visited == false){
          children += 1;
          g[vd].parent = v;
          dfs_fill(g, vd, v, time);
          g[v].low = std::min(g[v].low, g[vd].low);
          if(g[v].parent == -1 and children > 1){
            g[v].cutvertex = true;

          } else if(g[v].parent != -1 and g[vd].low >= g[v].disc){
            g[v].cutvertex = true;
          }
          if(g[vd].low > g[v].disc){
            g[boost::edge(v,vd,g).first].bridge = true;
          }
        }
        else if(g[v].parent != vd){
          g[v].low = std::min(g[v].low, g[vd].disc);
        }
    }
    time++;
}

void dfs(Graph &g, const Vertex& v, const Vertex& parent, long int& time, std::list<Edge>* st, int& bcc)
{
    time++;
    g[v].visited = true;
    g[v].disc = g[v].low = time+1;
    int children = 0;
    for (auto vd : boost::make_iterator_range(adjacent_vertices(v, g))) {
        if (g[vd].visited == false){
          children += 1;
          g[vd].parent = v;
          //save edge to stack
          st->push_back(boost::edge(v,vd,g).first);
          dfs(g, vd, v, time, st, bcc);

          g[v].low = std::min(g[v].low, g[vd].low);
          if(
            (g[v].parent == -1 and children > 1 ) or 
            (g[v].parent != -1 and g[vd].low >= g[v].disc)
          ){
            while(
              (st->back() != boost::edge(v, vd, g).first) or 
              (st->back() != boost::edge(vd, v, g).first)
            ){
              g[st->back()].bcc = bcc;
              st->pop_back();
            }
            g[st->back()].bcc = bcc;
            st->pop_back();
            bcc++;
          }
        }
        else if(g[v].parent != vd){
          g[v].low = std::min(g[v].low, g[vd].disc);
          if(g[vd].disc < g[v].disc){
            st->push_back(boost::edge(v, vd, g).first);
          }
        }
    }
    time++;
}
void compute_bcc (Graph &g, bool fill_cutvxs, bool fill_bridges)
{
  long int time = 0;
  if(fill_cutvxs or fill_bridges){
    dfs_fill(g, 0, -1, time);
  } else {
    std::list<Edge>* stack = new std::list<Edge>();
    int bcc = 1;
    for (auto vd : boost::make_iterator_range(vertices(g))){
      //guarantee every single node has been traversed by the dfs
      if (g[vd].visited == false){
        dfs(g, 0, -1, time, stack, bcc);
      }
      bool was_empty = true;
      //clean stack assigning last bccs
      while(stack->size() > 0){
        was_empty = false;
        g[stack->back()].bcc = bcc;
        stack->pop_back();
      }
    }
  }
}
