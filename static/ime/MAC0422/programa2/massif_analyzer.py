import os
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import glob
import argparse
import matplotlib.cm as cm
from matplotlib.colors import to_rgba

class MassifSnapshot:
    def __init__(self):
        self.snapshot_num = None
        self.time = None
        self.mem_heap_B = None
        self.mem_heap_extra_B = None
        self.mem_stacks_B = None
        self.heap_tree = None

class MassifData:
    def __init__(self, filename):
        self.filename = filename
        self.snapshots = []
        self.desc = ""
        self.cmd = ""
        self.time_unit = ""
        self.peak_mem = 0
        self.params = self.extract_parameters(filename)
        self.parse_file()
    
    def extract_parameters(self, filename):
        """Extract d, k, approach and iteration from filename."""
        # Parse pattern like massif_d500_k10_e_iter1.out
        pattern = r'massif_d(\d+)_k(\d+)_([ei])_iter(\d+)\.out'
        match = re.match(pattern, os.path.basename(filename))
        
        if match:
            return {
                'd': int(match.group(1)),  # Track size
                'k': int(match.group(2)),  # Number of cyclists
                'approach': 'efficient' if match.group(3) == 'e' else 'ingenuous',
                'iteration': int(match.group(4))
            }
        return None
    
    def parse_file(self):
        """Parse a massif output file."""
        current_snapshot = None
        
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Parse header information
            if line.startswith('desc:'):
                self.desc = line.split('desc:')[1].strip()
            elif line.startswith('cmd:'):
                self.cmd = line.split('cmd:')[1].strip()
                # Try to extract execution time from the command output if available
                time_match = re.search(r'time=(\d+\.\d+)', self.cmd)
                if time_match:
                    self.execution_time = float(time_match.group(1))
            elif line.startswith('time_unit:'):
                self.time_unit = line.split('time_unit:')[1].strip()
            
            # Start of a new snapshot
            elif line.startswith('#-----------') and i+1 < len(lines) and lines[i+1].strip().startswith('snapshot='):
                if current_snapshot is not None:
                    self.snapshots.append(current_snapshot)
                current_snapshot = MassifSnapshot()
                i += 1  # Move to the snapshot line
                current_snapshot.snapshot_num = int(lines[i].strip().split('=')[1])
            
            # Parse snapshot data
            elif line.startswith('time=') and current_snapshot is not None:
                current_snapshot.time = int(line.split('=')[1])
            elif line.startswith('mem_heap_B=') and current_snapshot is not None:
                current_snapshot.mem_heap_B = int(line.split('=')[1])
                # Update peak memory
                if current_snapshot.mem_heap_B > self.peak_mem:
                    self.peak_mem = current_snapshot.mem_heap_B
            elif line.startswith('mem_heap_extra_B=') and current_snapshot is not None:
                current_snapshot.mem_heap_extra_B = int(line.split('=')[1])
            elif line.startswith('mem_stacks_B=') and current_snapshot is not None:
                current_snapshot.mem_stacks_B = int(line.split('=')[1])
            elif line.startswith('heap_tree=') and current_snapshot is not None:
                current_snapshot.heap_tree = line.split('=')[1]
            
            i += 1
        
        # Add the last snapshot if it exists
        if current_snapshot is not None:
            self.snapshots.append(current_snapshot)

def group_data_by_parameters(data_list):
    """Group data by track size, cyclists, and approach."""
    grouped = {}
    
    for data in data_list:
        if data.params:
            key = (data.params['d'], data.params['k'], data.params['approach'])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(data)
    
    return grouped

def calculate_statistics(data_list):
    """Calculate statistics from a list of MassifData objects."""
    peak_memories = [data.peak_mem for data in data_list]
    
    stats_result = {
        'max': np.max(peak_memories),
        'mean': np.mean(peak_memories),
        'median': np.median(peak_memories),
        'std': np.std(peak_memories),
        'confidence_interval': stats.t.interval(0.95, len(peak_memories)-1, 
                                              loc=np.mean(peak_memories), 
                                              scale=stats.sem(peak_memories))
    }
    
    return stats_result

def categorize_parameters(grouped_data):
    """Categorize track sizes and cyclist numbers into small/medium/large and few/normal/many."""
    d_values = sorted(set(d for d, _, _ in grouped_data.keys()))
    k_values = sorted(set(k for _, k, _ in grouped_data.keys()))
    
    # Map actual values to categories
    if len(d_values) >= 3:
        d_categories = {
            d_values[0]: 'Small',
            d_values[len(d_values)//2]: 'Medium',
            d_values[-1]: 'Large'
        }
    else:
        d_categories = {d: f'Size {d}' for d in d_values}
    
    if len(k_values) >= 3:
        k_categories = {
            k_values[0]: 'Few',
            k_values[len(k_values)//2]: 'Normal',
            k_values[-1]: 'Many'
        }
    else:
        k_categories = {k: f'Cyclists {k}' for k in k_values}
    
    # Fill in any missing categories
    for d in d_values:
        if d not in d_categories:
            closest = min(d_categories.keys(), key=lambda x: abs(x - d))
            if d < closest:
                label = f'< {d_categories[closest]}'
            else:
                label = f'> {d_categories[closest]}'
            d_categories[d] = label
    
    for k in k_values:
        if k not in k_categories:
            closest = min(k_categories.keys(), key=lambda x: abs(x - k))
            if k < closest:
                label = f'< {k_categories[closest]}'
            else:
                label = f'> {k_categories[closest]}'
            k_categories[k] = label
    
    return d_categories, k_categories

def plot_memory_comparison_by_track_size(grouped_data, output_dir):
    """Plot memory usage comparison by track size."""
    plt.figure(figsize=(12, 8))
    plt.style.use('ggplot')
    
    d_categories, k_categories = categorize_parameters(grouped_data)
    
    # Generate color map - use nicer color palette
    num_k_values = len(set(k for _, k, _ in grouped_data.keys()))
    approach_colors = {
        'efficient': sns.color_palette("Blues_d", num_k_values),
        'ingenuous': sns.color_palette("Oranges_d", num_k_values)
    }
    
    # For each cyclist count and approach, plot memory vs track size
    for i, k in enumerate(sorted(set(k for _, k, _ in grouped_data.keys()))):
        for approach in ['efficient', 'ingenuous']:
            d_values = []
            means = []
            ci_errors = []
            
            for d in sorted(set(d for d, _, _ in grouped_data.keys())):
                key = (d, k, approach)
                if key in grouped_data and len(grouped_data[key]) > 0:
                    data_list = grouped_data[key]
                    stats_result = calculate_statistics(data_list)
                    
                    d_values.append(d)
                    means.append(stats_result['mean'] / 1024)  # Convert to KB
                    
                    # Calculate error bars for confidence interval
                    ci_low, ci_high = stats_result['confidence_interval']
                    ci_errors.append((stats_result['mean'] - ci_low) / 1024)
            
            if d_values:
                x_pos = np.arange(len(d_values))
                label = f"{k_categories[k]}, {'Efficient' if approach == 'efficient' else 'Ingenuous'}"
                color = approach_colors[approach][i]
                
                bars = plt.bar(x_pos + (0.2 if approach == 'efficient' else -0.2), means, 
                       width=0.4, yerr=ci_errors, capsize=5,
                       label=label, color=color, edgecolor='black', linewidth=1.5, alpha=0.65)
                
                # Add exact value labels on top of bars
                for bar_idx, bar in enumerate(bars):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{means[bar_idx]:.1f}',
                            ha='center', va='bottom', rotation=45, fontsize=8)
            
    plt.xlabel('Track Size (d)', fontweight='bold')
    plt.ylabel('Peak Memory Usage (KB)', fontweight='bold')
    plt.title('Memory Usage by Track Size', fontsize=14, fontweight='bold')
    plt.xticks(np.arange(len(d_categories)), [f"{d}\n({d_categories[d]})" for d in sorted(d_categories.keys())])
    plt.legend(loc='upper left', fontsize=8, framealpha=0.7)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add log scale option if there's large variation
    max_mean = max([m for _, _, a in grouped_data.keys() for m in [calculate_statistics(grouped_data[(_, _, a)])['mean'] / 1024 if (_, _, a) in grouped_data else 0]])
    min_mean = min([m for _, _, a in grouped_data.keys() for m in [calculate_statistics(grouped_data[(_, _, a)])['mean'] / 1024 if (_, _, a) in grouped_data and grouped_data[(_, _, a)] else float('inf')]])
    if max_mean / min_mean > 10:  # If range is more than 10x
        plt.yscale('log')
        plt.ylabel('Peak Memory Usage (KB) - Log Scale', fontweight='bold')
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'memory_by_track_size.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_memory_comparison_by_cyclists(grouped_data, output_dir):
    """Plot memory usage comparison by number of cyclists."""
    plt.figure(figsize=(12, 8))
    plt.style.use('ggplot')
    
    d_categories, k_categories = categorize_parameters(grouped_data)
    
    # Generate color map with nicer color palette
    num_d_values = len(set(d for d, _, _ in grouped_data.keys()))
    approach_colors = {
        'efficient': sns.color_palette("Blues_d", num_d_values),
        'ingenuous': sns.color_palette("Oranges_d", num_d_values)
    }
    
    # For each track size and approach, plot memory vs cyclists
    for i, d in enumerate(sorted(set(d for d, _, _ in grouped_data.keys()))):
        for approach in ['efficient', 'ingenuous']:
            k_values = []
            means = []
            ci_errors = []
            
            for k in sorted(set(k for _, k, _ in grouped_data.keys())):
                key = (d, k, approach)
                if key in grouped_data and len(grouped_data[key]) > 0:
                    data_list = grouped_data[key]
                    stats_result = calculate_statistics(data_list)
                    
                    k_values.append(k)
                    means.append(stats_result['mean'] / 1024)  # Convert to KB
                    
                    # Calculate error bars for confidence interval
                    ci_low, ci_high = stats_result['confidence_interval']
                    ci_errors.append((stats_result['mean'] - ci_low) / 1024)
            
            if k_values:
                x_pos = np.arange(len(k_values))
                label = f"{d_categories[d]}, {'Efficient' if approach == 'efficient' else 'Ingenuous'}"
                color = approach_colors[approach][i]
                
                bars = plt.bar(x_pos + (0.2 if approach == 'efficient' else -0.2), means, 
                       width=0.4, yerr=ci_errors, capsize=5,
                       label=label, color=color, edgecolor='black', linewidth=1.5, alpha=0.65)
                
                # Add exact value labels on top of bars
                for bar_idx, bar in enumerate(bars):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{means[bar_idx]:.1f}',
                            ha='center', va='bottom', rotation=45, fontsize=8)
            
    plt.xlabel('Number of Cyclists (k)', fontweight='bold')
    plt.ylabel('Peak Memory Usage (KB)', fontweight='bold')
    plt.title('Memory Usage by Number of Cyclists', fontsize=14, fontweight='bold')
    plt.xticks(np.arange(len(k_categories)), [f"{k}\n({k_categories[k]})" for k in sorted(k_categories.keys())])
    plt.legend(loc='upper left', fontsize=8, framealpha=0.7)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add log scale option if there's large variation
    max_mean = max([m for _, _, a in grouped_data.keys() for m in [calculate_statistics(grouped_data[(_, _, a)])['mean'] / 1024 if (_, _, a) in grouped_data else 0]])
    min_mean = min([m for _, _, a in grouped_data.keys() for m in [calculate_statistics(grouped_data[(_, _, a)])['mean'] / 1024 if (_, _, a) in grouped_data and grouped_data[(_, _, a)] else float('inf')]])
    if max_mean / min_mean > 10:  # If range is more than 10x
        plt.yscale('log')
        plt.ylabel('Peak Memory Usage (KB) - Log Scale', fontweight='bold')
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'memory_by_cyclists.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_memory_comparison_by_approach(grouped_data, output_dir):
    """Plot memory usage comparison by approach (efficient vs ingenuous)."""
    plt.figure(figsize=(15, 10))
    plt.style.use('ggplot')
    
    d_categories, k_categories = categorize_parameters(grouped_data)
    
    # Create a grid of parameter combinations
    combinations = []
    for d in sorted(set(d for d, _, _ in grouped_data.keys())):
        for k in sorted(set(k for _, k, _ in grouped_data.keys())):
            combinations.append((d, k))
    
    x_pos = np.arange(len(combinations))
    efficient_means = []
    efficient_errors = []
    ingenuous_means = []
    ingenuous_errors = []
    
    for d, k in combinations:
        # Efficient approach
        key = (d, k, 'efficient')
        if key in grouped_data and len(grouped_data[key]) > 0:
            stats_result = calculate_statistics(grouped_data[key])
            efficient_means.append(stats_result['mean'] / 1024)  # Convert to KB
            ci_low, ci_high = stats_result['confidence_interval']
            efficient_errors.append((stats_result['mean'] - ci_low) / 1024)
        else:
            efficient_means.append(0)
            efficient_errors.append(0)
        
        # Ingenuous approach
        key = (d, k, 'ingenuous')
        if key in grouped_data and len(grouped_data[key]) > 0:
            stats_result = calculate_statistics(grouped_data[key])
            ingenuous_means.append(stats_result['mean'] / 1024)  # Convert to KB
            ci_low, ci_high = stats_result['confidence_interval']
            ingenuous_errors.append((stats_result['mean'] - ci_low) / 1024)
        else:
            ingenuous_means.append(0)
            ingenuous_errors.append(0)
    
    # Create grouped bar chart with better colors
    bars1 = plt.bar(x_pos - 0.2, efficient_means, width=0.4, yerr=efficient_errors, 
                   capsize=5, label='Efficient Approach', color='#3274A1', edgecolor='black', alpha=0.85)
    bars2 = plt.bar(x_pos + 0.2, ingenuous_means, width=0.4, yerr=ingenuous_errors, 
                   capsize=5, label='Ingenuous Approach', color='#E1812C', edgecolor='black', alpha=0.85)
    
    # Add exact value labels on top of bars
    for i, bar in enumerate(bars1):
        if efficient_means[i] > 0:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{efficient_means[i]:.1f}',
                    ha='center', va='bottom', rotation=45, fontsize=8)
    
    for i, bar in enumerate(bars2):
        if ingenuous_means[i] > 0:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{ingenuous_means[i]:.1f}',
                    ha='center', va='bottom', rotation=45, fontsize=8)
    
    plt.xlabel('Parameter Combination (d, k)', fontweight='bold')
    plt.ylabel('Peak Memory Usage (KB)', fontweight='bold')
    plt.title('Memory Usage: Efficient vs Ingenuous Approach', fontsize=14, fontweight='bold')
    plt.xticks(x_pos, [f"d={d}\nk={k}" for d, k in combinations], rotation=45)
    plt.legend(loc='upper left', fontsize=10, framealpha=0.7)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add log scale option if there's large variation
    max_val = max(max(efficient_means), max(ingenuous_means))
    min_val = min([v for v in efficient_means + ingenuous_means if v > 0] or [1])
    if max_val / min_val > 10:  # If range is more than 10x
        plt.yscale('log')
        plt.ylabel('Peak Memory Usage (KB) - Log Scale', fontweight='bold')
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'memory_by_approach.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_memory_usage_over_time(data_list, output_dir):
    """Plot memory usage over time, split by approach and other parameters."""
    # Group data by parameters
    grouped_data = group_data_by_parameters(data_list)
    
    # Create separate directories for the time plots
    time_plots_dir = os.path.join(output_dir, 'time_plots')
    os.makedirs(time_plots_dir, exist_ok=True)
    
    # First, create separate plots by approach
    for approach in ['efficient', 'ingenuous']:
        approach_dir = os.path.join(time_plots_dir, approach)
        os.makedirs(approach_dir, exist_ok=True)
        
        # Get all parameter combinations for this approach
        approach_combinations = [(d, k) for d, k, a in grouped_data.keys() if a == approach]
        
        # 1. Plot by track size (d) - one plot per d, with different k values
        d_values = sorted(set(d for d, _ in approach_combinations))
        for d in d_values:
            plt.figure(figsize=(10, 6))
            plt.style.use('ggplot')
            
            # Use color palette that's visually distinct
            k_values_for_this_d = [k for _, k in approach_combinations if k > 0]
            if not k_values_for_this_d:
                plt.close()
                continue
                
            colors = sns.color_palette("husl", len(set(k_values_for_this_d)))
            
            i = 0
            has_data = False
            for k in sorted(set(k for _, k in approach_combinations)):
                key = (d, k, approach)
                if key in grouped_data and grouped_data[key]:
                    has_data = True
                    data = grouped_data[key][0]  # Take first run
                    times = [snapshot.time for snapshot in data.snapshots]
                    mem_usage = [snapshot.mem_heap_B / 1024 for snapshot in data.snapshots]  # KB
                    
                    plt.plot(times, mem_usage, label=f"k={k}", 
                            color=colors[i % len(colors)], linewidth=2.5, alpha=0.8)
                    
                    # Mark peak memory
                    peak_idx = mem_usage.index(max(mem_usage))
                    plt.plot(times[peak_idx], mem_usage[peak_idx], 'o', 
                           color=to_rgba(colors[i % len(colors)], 1.0),
                           markersize=6)
                    plt.annotate(f"{mem_usage[peak_idx]:.1f} KB", 
                              (times[peak_idx], mem_usage[peak_idx]),
                              textcoords="offset points", 
                              xytext=(0,10), 
                              ha='center',
                              fontsize=8,
                              bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
                    i += 1
            
            # Only proceed if we've added data to the plot
            if has_data:
                plt.xlabel('Time Units', fontweight='bold')
                plt.ylabel('Memory Usage (KB)', fontweight='bold')
                plt.title(f'Memory Over Time - {approach.capitalize()} Approach, Track Size d={d}', 
                        fontsize=14, fontweight='bold')
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Only add legend if we have data points with labels
                if i > 0:
                    plt.legend(loc='best', framealpha=0.7, fontsize=10)
                
                plt.tight_layout()
                
                plt.savefig(os.path.join(approach_dir, f'memory_time_d{d}.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Plot by cyclists (k) - one plot per k, with different d values
        k_values = sorted(set(k for _, k in approach_combinations))
        for k in k_values:
            plt.figure(figsize=(10, 6))
            plt.style.use('ggplot')
            
            # Use color palette that's visually distinct
            d_values_for_this_k = [d for d, _ in approach_combinations if d > 0]
            if not d_values_for_this_k:
                plt.close()
                continue
                
            colors = sns.color_palette("viridis", len(set(d_values_for_this_k)))
            
            i = 0
            has_data = False
            valid_d_values = sorted(set(d for d, _ in approach_combinations))
            for d in valid_d_values:
                key = (d, k, approach)
                if key in grouped_data and grouped_data[key]:
                    has_data = True
                    data = grouped_data[key][0]  # Take first run
                    times = [snapshot.time for snapshot in data.snapshots]
                    mem_usage = [snapshot.mem_heap_B / 1024 for snapshot in data.snapshots]  # KB
                    
                    plt.plot(times, mem_usage, label=f"d={d}", 
                            color=colors[i % len(colors)], linewidth=2.5, alpha=0.8)
                    
                    # Mark peak memory
                    peak_idx = mem_usage.index(max(mem_usage))
                    plt.plot(times[peak_idx], mem_usage[peak_idx], 'o', 
                           color=to_rgba(colors[i % len(colors)], 1.0),
                           markersize=6)
                    plt.annotate(f"{mem_usage[peak_idx]:.1f} KB", 
                              (times[peak_idx], mem_usage[peak_idx]),
                              textcoords="offset points", 
                              xytext=(0,10), 
                              ha='center',
                              fontsize=8,
                              bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
                    i += 1
            
            # Only proceed if we've added data to the plot
            if has_data:
                plt.xlabel('Time Units', fontweight='bold')
                plt.ylabel('Memory Usage (KB)', fontweight='bold')
                plt.title(f'Memory Over Time - {approach.capitalize()} Approach, Cyclists k={k}', 
                        fontsize=14, fontweight='bold')
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Only add legend if we have data points with labels
                if i > 0:
                    plt.legend(loc='best', framealpha=0.7, fontsize=10)
                
                plt.tight_layout()
                
                plt.savefig(os.path.join(approach_dir, f'memory_time_k{k}.png'), dpi=300, bbox_inches='tight')
            plt.close()
    
    # 3. Generate an index plot that shows a few key comparisons
    plt.figure(figsize=(12, 8))
    plt.style.use('ggplot')
    
    # Select a few representative combinations for the summary plot
    d_values = sorted(set(d for d, _, _ in grouped_data.keys()))
    k_values = sorted(set(k for _, k, _ in grouped_data.keys()))
    
    has_data = False
    if d_values and k_values:
        # Choose a medium track size and medium cyclist count if available
        mid_d = d_values[len(d_values)//2] if len(d_values) > 2 else d_values[0]
        mid_k = k_values[len(k_values)//2] if len(k_values) > 2 else k_values[0]
        
        # Plot comparison for same d, k with different approaches
        for approach, color, style in [('efficient', '#1f77b4', '-'), ('ingenuous', '#ff7f0e', '--')]:
            key = (mid_d, mid_k, approach)
            if key in grouped_data and grouped_data[key]:
                has_data = True
                data = grouped_data[key][0]
                times = [snapshot.time for snapshot in data.snapshots]
                mem_usage = [snapshot.mem_heap_B / 1024 for snapshot in data.snapshots]
                
                plt.plot(times, mem_usage, 
                       label=f"{approach.capitalize()}, d={mid_d}, k={mid_k}",
                       color=color, linestyle=style, linewidth=2.5, alpha=0.8)
    
    if has_data:
        plt.xlabel('Time Units', fontweight='bold')
        plt.ylabel('Memory Usage (KB)', fontweight='bold')
        plt.title('Memory Usage Comparison Over Time (Sample)', fontsize=14, fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='best', framealpha=0.7, fontsize=10)
        plt.tight_layout()
        
        plt.savefig(os.path.join(time_plots_dir, 'memory_comparison_sample.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create an index.html file to navigate the various time plots
    try:
        with open(os.path.join(time_plots_dir, 'index.html'), 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Memory Usage Over Time Analysis</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1, h2 { color: #333; }
                    .section { margin-bottom: 30px; }
                    .plot-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
                    .plot-item { border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
                    .plot-item img { max-width: 100%; height: auto; }
                    .plot-item p { margin: 10px 0 5px; }
                    .no-data { color: #999; font-style: italic; }
                </style>
            </head>
            <body>
                <h1>Memory Usage Over Time Analysis</h1>
            """)
            
            # Check if we have any plots for efficient approach
            efficient_plots = []
            for d in d_values:
                if os.path.exists(os.path.join(time_plots_dir, 'efficient', f'memory_time_d{d}.png')):
                    efficient_plots.append((d, 'd'))
            
            for k in k_values:
                if os.path.exists(os.path.join(time_plots_dir, 'efficient', f'memory_time_k{k}.png')):
                    efficient_plots.append((k, 'k'))
            
            f.write("""
                <div class="section">
                    <h2>Efficient Approach</h2>
            """)
            
            if efficient_plots:
                f.write('<div class="plot-grid">')
                # Add links to efficient approach plots
                for value, param_type in efficient_plots:
                    if param_type == 'd':
                        f.write(f"""
                        <div class="plot-item">
                            <p>Track Size d={value}</p>
                            <a href="efficient/memory_time_d{value}.png" target="_blank">
                                <img src="efficient/memory_time_d{value}.png" alt="Memory usage for d={value}">
                            </a>
                        </div>
                        """)
                    else:  # k
                        f.write(f"""
                        <div class="plot-item">
                            <p>Cyclists k={value}</p>
                            <a href="efficient/memory_time_k{value}.png" target="_blank">
                                <img src="efficient/memory_time_k{value}.png" alt="Memory usage for k={value}">
                            </a>
                        </div>
                        """)
                f.write('</div>')
            else:
                f.write('<p class="no-data">No data available for efficient approach.</p>')
            
            f.write('</div>')  # End of efficient section
            
            # Check if we have any plots for ingenuous approach
            ingenuous_plots = []
            for d in d_values:
                if os.path.exists(os.path.join(time_plots_dir, 'ingenuous', f'memory_time_d{d}.png')):
                    ingenuous_plots.append((d, 'd'))
            
            for k in k_values:
                if os.path.exists(os.path.join(time_plots_dir, 'ingenuous', f'memory_time_k{k}.png')):
                    ingenuous_plots.append((k, 'k'))
            
            f.write("""
                <div class="section">
                    <h2>Ingenuous Approach</h2>
            """)
            
            if ingenuous_plots:
                f.write('<div class="plot-grid">')
                # Add links to ingenuous approach plots
                for value, param_type in ingenuous_plots:
                    if param_type == 'd':
                        f.write(f"""
                        <div class="plot-item">
                            <p>Track Size d={value}</p>
                            <a href="ingenuous/memory_time_d{value}.png" target="_blank">
                                <img src="ingenuous/memory_time_d{value}.png" alt="Memory usage for d={value}">
                            </a>
                        </div>
                        """)
                    else:  # k
                        f.write(f"""
                        <div class="plot-item">
                            <p>Cyclists k={value}</p>
                            <a href="ingenuous/memory_time_k{value}.png" target="_blank">
                                <img src="ingenuous/memory_time_k{value}.png" alt="Memory usage for k={value}">
                            </a>
                        </div>
                        """)
                f.write('</div>')
            else:
                f.write('<p class="no-data">No data available for ingenuous approach.</p>')
            
            f.write('</div>')  # End of ingenuous section
            
            # Add comparison plot if it exists
            if os.path.exists(os.path.join(time_plots_dir, 'memory_comparison_sample.png')):
                f.write("""
                <div class="section">
                    <h2>Approach Comparison</h2>
                    <div style="text-align: center;">
                        <a href="memory_comparison_sample.png" target="_blank">
                            <img src="memory_comparison_sample.png" alt="Memory usage comparison" style="max-width: 80%; height: auto;">
                        </a>
                    </div>
                </div>
                """)
            
            f.write("""
            </body>
            </html>
            """)
    except Exception as e:
        print(f"Error creating index.html: {e}")
    
    print(f"Time plots saved to: {time_plots_dir}")
    print(f"Open {time_plots_dir}/index.html to navigate the plots")

def generate_summary_table(grouped_data, output_dir):
    """Generate a summary table with all statistics."""
    d_categories, k_categories = categorize_parameters(grouped_data)
    
    with open(os.path.join(output_dir, 'summary_statistics.txt'), 'w') as f:
        f.write("Summary Statistics for Memory Usage (in KB)\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("{:<10} {:<10} {:<15} {:<12} {:<12} {:<12} {:<20}\n".format(
            "Track (d)", "Cyclists (k)", "Approach", "Mean (KB)", "Median (KB)", "Std Dev (KB)", "95% CI (KB)"))
        f.write("-" * 80 + "\n")
        
        for d in sorted(set(d for d, _, _ in grouped_data.keys())):
            for k in sorted(set(k for _, k, _ in grouped_data.keys())):
                for approach in ['efficient', 'ingenuous']:
                    key = (d, k, approach)
                    if key in grouped_data and len(grouped_data[key]) > 0:
                        data_list = grouped_data[key]
                        stats_result = calculate_statistics(data_list)
                        
                        ci_low, ci_high = stats_result['confidence_interval']
                        ci_str = "[{:.2f}, {:.2f}]".format(ci_low/1024, ci_high/1024)
                        
                        f.write("{:<10} {:<10} {:<15} {:<12.2f} {:<12.2f} {:<12.2f} {:<20}\n".format(
                            d, k, approach,
                            stats_result['mean']/1024,
                            stats_result['median']/1024,
                            stats_result['std']/1024,
                            ci_str))
            f.write("-" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Analyze massif memory profiling outputs for cyclist simulation.')
    parser.add_argument('--input', '-i', required=True, help='Input directory containing massif output files')
    parser.add_argument('--output', '-o', default='massif_analysis', help='Output directory for graphs and analysis')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Get list of files
    file_list = glob.glob(os.path.join(args.input, '*.out'))
    
    if not file_list:
        print(f"No massif output files found in: {args.input}")
        return
    
    print(f"Found {len(file_list)} massif output files")
    
    # Parse all files
    data_list = []
    for file in file_list:
        print(f"Processing: {os.path.basename(file)}")
        data_list.append(MassifData(file))
    
    # Group data by parameters
    grouped_data = group_data_by_parameters(data_list)
    print(f"Grouped into {len(grouped_data)} parameter combinations")
    
    # Generate plots
    plot_memory_comparison_by_track_size(grouped_data, args.output)
    plot_memory_comparison_by_cyclists(grouped_data, args.output)
    plot_memory_comparison_by_approach(grouped_data, args.output)
    plot_memory_usage_over_time(data_list, args.output)
    
    # Generate summary table
    generate_summary_table(grouped_data, args.output)
    
    print(f"Analysis complete. Results saved to: {args.output}")

if __name__ == "__main__":
    main()