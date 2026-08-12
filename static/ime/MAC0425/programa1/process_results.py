import os
import re

resultados_dir = 'resultados'
files = [f for f in os.listdir(resultados_dir) if f.endswith('.txt') and (f.startswith('dfs') or f.startswith('bfs') or f.startswith('ucs') or f.startswith('astar') or f.startswith('iddfs') or f.startswith('lrta'))]

summary = ""

for file in sorted(files):
    filepath = os.path.join(resultados_dir, file)
    with open(filepath, 'r') as f:
        content = f.read()
    
    cost = re.search(r'cost of (\d+)', content)
    expanded = re.search(r'Search nodes expanded: (\d+)', content)
    estimate = re.search(r'Final H-value of the initial state: ([\d\.]+)', content)
    
    cost_val = cost.group(1) if cost else 'N/A'
    exp_val = expanded.group(1) if expanded else 'N/A'
    est_val = estimate.group(1) if estimate else 'N/A'
    
    if "lrta" in file:
        summary += f"- **{file}**: Cost={cost_val}, Expanded={exp_val}, StartEstimate={est_val}\n"
    else:
        summary += f"- **{file}**: Cost={cost_val}, Expanded={exp_val}\n"

with open(os.path.join(resultados_dir, 'summary.md'), 'w') as f:
    f.write(summary)

print("Summary generated.")
