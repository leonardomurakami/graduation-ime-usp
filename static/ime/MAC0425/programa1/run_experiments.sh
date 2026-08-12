#!/bin/bash

mkdir -p resultados

echo "Running DFS experiments..."
python pacman.py -q -l tinyMaze -p SearchAgent > resultados/dfs_tinyMaze.txt
python pacman.py -q -l mediumMaze -p SearchAgent > resultados/dfs_mediumMaze.txt
python pacman.py -q -l bigMaze -z .5 -p SearchAgent > resultados/dfs_bigMaze.txt

echo "Running BFS experiments..."
python pacman.py -q -l tinyMaze -p SearchAgent -a fn=bfs > resultados/bfs_tinyMaze.txt
python pacman.py -q -l mediumMaze -p SearchAgent -a fn=bfs > resultados/bfs_mediumMaze.txt
python pacman.py -q -l bigMaze -p SearchAgent -a fn=bfs -z .5 > resultados/bfs_bigMaze.txt

echo "Running UCS experiments..."
python pacman.py -q -l mediumMaze -p SearchAgent -a fn=ucs > resultados/ucs_mediumMaze.txt
python pacman.py -q -l mediumDottedMaze -p StayEastSearchAgent > resultados/ucs_mediumDottedMaze_StayEast.txt
python pacman.py -q -l mediumScaryMaze -p StayWestSearchAgent > resultados/ucs_mediumScaryMaze_StayWest.txt

echo "Running A* experiments..."
python pacman.py -q -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic > resultados/astar_bigMaze.txt
python pacman.py -q -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic > resultados/astar_mediumMaze.txt
python pacman.py -q -l tinyMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic > resultados/astar_tinyMaze.txt

echo "Running ID-DFS experiments..."
python pacman.py -q -l tinyMaze -p SearchAgent -a fn=iddfs > resultados/iddfs_tinyMaze.txt
python pacman.py -q -l mediumMaze -p SearchAgent -a fn=iddfs > resultados/iddfs_mediumMaze.txt
python pacman.py -q -l bigMaze -p SearchAgent -a fn=iddfs -z .5 > resultados/iddfs_bigMaze.txt

echo "Running LRTA* experiments (nullHeuristic)..."
for trials in 10 30 50 100 150; do
    python pacman.py -q -l mediumMaze -p SearchAgent -a fn=lrta,trials=$trials > resultados/lrta_null_$trials.txt
done

echo "Running LRTA* experiments (manhattanHeuristic)..."
for trials in 10 30 50 100 150; do
    python pacman.py -q -l mediumMaze -p SearchAgent -a fn=lrta,heuristic=manhattanHeuristic,trials=$trials > resultados/lrta_manhattan_$trials.txt
done

echo "Running Scenario 2 - Corners BFS..."
python pacman.py -q -l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem > resultados/bfs_tinyCorners.txt
python pacman.py -q -l mediumCorners -p SearchAgent -a fn=bfs,prob=CornersProblem > resultados/bfs_mediumCorners.txt
python pacman.py -q -l bigCorners -z 0.5 -p SearchAgent -a fn=bfs,prob=CornersProblem > resultados/bfs_bigCorners.txt

echo "Running Scenario 2 - Corners A*..."
python pacman.py -q -l tinyCorners -p AStarCornersAgent > resultados/astar_tinyCorners.txt
python pacman.py -q -l mediumCorners -p AStarCornersAgent > resultados/astar_mediumCorners.txt
python pacman.py -q -l bigCorners -z 0.5 -p AStarCornersAgent > resultados/astar_bigCorners.txt

echo "Running Scenario 2 - LRTA* Corners..."
python pacman.py -q -l tinyCorners -p LRTAStarCornersAgent -a trials=80 > resultados/lrta_tinyCorners.txt

echo "All experiments finished!"
