import os
import re
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class TimeData:
    def __init__(self, filename):
        self.filename = filename
        self.command = ""
        self.user_time = 0.0
        self.system_time = 0.0
        self.cpu_percent = 0.0
        self.elapsed_time = 0.0
        self.max_resident_set_size = 0
        self.voluntary_ctx_switches = 0
        self.involuntary_ctx_switches = 0
        self.params = self.extract_parameters(filename)
        self.parse_file()

    def extract_parameters(self, filename):
        """Extract d, k, approach and iteration from filename."""
        # Parse pattern like time_d500_k10_e_iter1.txt
        pattern = r'time_d(\d+)_k(\d+)_([ei])_iter(\d+)\.txt'
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
        """Parse a time command output file."""
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            # Parse the command
            if line.startswith("Command being timed:"):
                self.command = line.split(":", 1)[1].strip()
            
            # Parse user time
            elif line.startswith("User time (seconds):"):
                self.user_time = float(line.split(":", 1)[1].strip())
            
            # Parse system time
            elif line.startswith("System time (seconds):"):
                self.system_time = float(line.split(":", 1)[1].strip())
            
            # Parse CPU usage percentage
            elif line.startswith("Percent of CPU this job got:"):
                self.cpu_percent = float(line.split(":", 1)[1].strip().replace("%", ""))
            
            # Parse elapsed (wall clock) time
            elif line.startswith("Elapsed (wall clock) time"):
                # Extract the time value after the format description and colon
                match = re.search(r'Elapsed \(wall clock\) time.*?: ([\d:\.]+)', line)
                if match:
                    time_str = match.group(1)
                    
                    # Parse time formats like 0:00.27 or 0:00:00.27
                    parts = time_str.split(":")
                    if len(parts) == 2:  # Format: m:ss.ms
                        minutes, seconds = parts
                        self.elapsed_time = float(minutes) * 60 + float(seconds)
                    elif len(parts) == 3:  # Format: h:mm:ss.ms
                        hours, minutes, seconds = parts
                        self.elapsed_time = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
                    else:
                        # Single value
                        self.elapsed_time = float(time_str)
                else:
                    # Fallback if regex doesn't match
                    self.elapsed_time = 0.0
            
            # Parse maximum resident set size
            elif line.startswith("Maximum resident set size (kbytes):"):
                self.max_resident_set_size = int(line.split(":", 1)[1].strip())
            
            # Parse voluntary context switches
            elif line.startswith("Voluntary context switches:"):
                self.voluntary_ctx_switches = int(line.split(":", 1)[1].strip())
            
            # Parse involuntary context switches
            elif line.startswith("Involuntary context switches:"):
                self.involuntary_ctx_switches = int(line.split(":", 1)[1].strip())

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

def calculate_statistics(data_list, metric):
    """Calculate statistics for a specific metric from a list of TimeData objects."""
    values = [getattr(data, metric) for data in data_list]
    
    stats_result = {
        'max': np.max(values),
        'min': np.min(values),
        'mean': np.mean(values),
        'median': np.median(values),
        'std': np.std(values),
        'confidence_interval': stats.t.interval(0.95, len(values)-1, 
                                              loc=np.mean(values), 
                                              scale=stats.sem(values))
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

def plot_time_comparison_by_track_size(grouped_data, output_dir, metric_name, metric, y_label):
    """Plot time comparison by track size for a specific metric."""
    plt.figure(figsize=(12, 8))
    plt.style.use('ggplot')
    
    d_categories, k_categories = categorize_parameters(grouped_data)
    
    # Generate color map - use nicer color palette
    num_k_values = len(set(k for _, k, _ in grouped_data.keys()))
    approach_colors = {
        'efficient': sns.color_palette("Blues_d", num_k_values),
        'ingenuous': sns.color_palette("Oranges_d", num_k_values)
    }
    
    # For each cyclist count and approach, plot time vs track size
    for i, k in enumerate(sorted(set(k for _, k, _ in grouped_data.keys()))):
        for approach in ['efficient', 'ingenuous']:
            d_values = []
            means = []
            ci_errors = []
            
            for d in sorted(set(d for d, _, _ in grouped_data.keys())):
                key = (d, k, approach)
                if key in grouped_data and len(grouped_data[key]) > 0:
                    data_list = grouped_data[key]
                    stats_result = calculate_statistics(data_list, metric)
                    
                    d_values.append(d)
                    means.append(stats_result['mean'])
                    
                    # Calculate error bars for confidence interval
                    ci_low, ci_high = stats_result['confidence_interval']
                    ci_errors.append(stats_result['mean'] - ci_low)
            
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
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                            f'{means[bar_idx]:.3f}',
                            ha='center', va='bottom', rotation=45, fontsize=8)
            
    plt.xlabel('Track Size (d)', fontweight='bold')
    plt.ylabel(y_label, fontweight='bold')
    plt.title(f'{metric_name} by Track Size', fontsize=14, fontweight='bold')
    plt.xticks(np.arange(len(d_categories)), [f"{d}\n({d_categories[d]})" for d in sorted(d_categories.keys())])
    plt.legend(loc='upper left', fontsize=8, framealpha=0.7)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, f'{metric}_by_track_size.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_time_comparison_by_cyclists(grouped_data, output_dir, metric_name, metric, y_label):
    """Plot time comparison by number of cyclists for a specific metric."""
    plt.figure(figsize=(12, 8))
    plt.style.use('ggplot')
    
    d_categories, k_categories = categorize_parameters(grouped_data)
    
    # Generate color map with nicer color palette
    num_d_values = len(set(d for d, _, _ in grouped_data.keys()))
    approach_colors = {
        'efficient': sns.color_palette("Blues_d", num_d_values),
        'ingenuous': sns.color_palette("Oranges_d", num_d_values)
    }
    
    # For each track size and approach, plot time vs cyclists
    for i, d in enumerate(sorted(set(d for d, _, _ in grouped_data.keys()))):
        for approach in ['efficient', 'ingenuous']:
            k_values = []
            means = []
            ci_errors = []
            
            for k in sorted(set(k for _, k, _ in grouped_data.keys())):
                key = (d, k, approach)
                if key in grouped_data and len(grouped_data[key]) > 0:
                    data_list = grouped_data[key]
                    stats_result = calculate_statistics(data_list, metric)
                    
                    k_values.append(k)
                    means.append(stats_result['mean'])
                    
                    # Calculate error bars for confidence interval
                    ci_low, ci_high = stats_result['confidence_interval']
                    ci_errors.append(stats_result['mean'] - ci_low)
            
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
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                            f'{means[bar_idx]:.3f}',
                            ha='center', va='bottom', rotation=45, fontsize=8)
            
    plt.xlabel('Number of Cyclists (k)', fontweight='bold')
    plt.ylabel(y_label, fontweight='bold')
    plt.title(f'{metric_name} by Number of Cyclists', fontsize=14, fontweight='bold')
    plt.xticks(np.arange(len(k_categories)), [f"{k}\n({k_categories[k]})" for k in sorted(k_categories.keys())])
    plt.legend(loc='upper left', fontsize=8, framealpha=0.7)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, f'{metric}_by_cyclists.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_time_comparison_by_approach(grouped_data, output_dir, metric_name, metric, y_label):
    """Plot time comparison by approach (efficient vs ingenuous) for a specific metric."""
    plt.figure(figsize=(15, 10))
    plt.style.use('ggplot')
    
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
            stats_result = calculate_statistics(grouped_data[key], metric)
            efficient_means.append(stats_result['mean'])
            ci_low, ci_high = stats_result['confidence_interval']
            efficient_errors.append(stats_result['mean'] - ci_low)
        else:
            efficient_means.append(0)
            efficient_errors.append(0)
        
        # Ingenuous approach
        key = (d, k, 'ingenuous')
        if key in grouped_data and len(grouped_data[key]) > 0:
            stats_result = calculate_statistics(grouped_data[key], metric)
            ingenuous_means.append(stats_result['mean'])
            ci_low, ci_high = stats_result['confidence_interval']
            ingenuous_errors.append(stats_result['mean'] - ci_low)
        else:
            ingenuous_means.append(0)
            ingenuous_errors.append(0)
    
    # Create grouped bar chart with better colors
    bars1 = plt.bar(x_pos - 0.2, efficient_means, width=0.4, yerr=efficient_errors, 
                   capsize=5, label='Efficient Approach', color='#3274A1', edgecolor='black', linewidth=1.5, alpha=0.65)
    bars2 = plt.bar(x_pos + 0.2, ingenuous_means, width=0.4, yerr=ingenuous_errors, 
                   capsize=5, label='Ingenuous Approach', color='#E1812C', edgecolor='black', linewidth=1.5, alpha=0.65)
    
    # Add exact value labels on top of bars
    for i, bar in enumerate(bars1):
        if efficient_means[i] > 0:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{efficient_means[i]:.3f}',
                    ha='center', va='bottom', rotation=45, fontsize=8)
    
    for i, bar in enumerate(bars2):
        if ingenuous_means[i] > 0:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{ingenuous_means[i]:.3f}',
                    ha='center', va='bottom', rotation=45, fontsize=8)
    
    plt.xlabel('Parameter Combination (d, k)', fontweight='bold')
    plt.ylabel(y_label, fontweight='bold')
    plt.title(f'{metric_name}: Efficient vs Ingenuous Approach', fontsize=14, fontweight='bold')
    plt.xticks(x_pos, [f"d={d}\nk={k}" for d, k in combinations], rotation=45)
    plt.legend(loc='upper left', fontsize=10, framealpha=0.7)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, f'{metric}_by_approach.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_context_switches(grouped_data, output_dir):
    """Plot voluntary vs involuntary context switches."""
    plt.figure(figsize=(15, 10))
    plt.style.use('ggplot')
    
    # Create a grid of parameter combinations
    combinations = []
    for d in sorted(set(d for d, _, _ in grouped_data.keys())):
        for k in sorted(set(k for _, k, _ in grouped_data.keys())):
            for approach in ['efficient', 'ingenuous']:
                combinations.append((d, k, approach))
    
    x_pos = np.arange(len(combinations))
    voluntary_means = []
    involuntary_means = []
    labels = []
    
    for d, k, approach in combinations:
        key = (d, k, approach)
        labels.append(f"d={d}, k={k}\n{approach}")
        
        if key in grouped_data and len(grouped_data[key]) > 0:
            vol_stats = calculate_statistics(grouped_data[key], 'voluntary_ctx_switches')
            invol_stats = calculate_statistics(grouped_data[key], 'involuntary_ctx_switches')
            
            voluntary_means.append(vol_stats['mean'])
            involuntary_means.append(invol_stats['mean'])
        else:
            voluntary_means.append(0)
            involuntary_means.append(0)
    
    # Create grouped bar chart
    width = 0.35
    fig, ax = plt.subplots(figsize=(15, 10))
    
    voluntary_bars = ax.bar(x_pos - width/2, voluntary_means, width, label='Voluntary', color='#3274A1', edgecolor='black', linewidth=1.5, alpha=0.65)
    involuntary_bars = ax.bar(x_pos + width/2, involuntary_means, width, label='Involuntary', color='#E1812C', edgecolor='black', linewidth=1.5, alpha=0.65)
    
    # Add some text for labels, title and axes ticks
    ax.set_xlabel('Parameter Combination (d, k, approach)', fontweight='bold')
    ax.set_ylabel('Number of Context Switches', fontweight='bold')
    ax.set_title('Voluntary vs Involuntary Context Switches', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45)
    ax.legend()
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'context_switches.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_summary_table(grouped_data, output_dir):
    """Generate a summary table with all time statistics."""
    with open(os.path.join(output_dir, 'time_summary_statistics.txt'), 'w') as f:
        f.write("Summary Statistics for Execution Time\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("{:<8} {:<8} {:<12} {:<15} {:<15} {:<15} {:<15} {:<15}\n".format(
            "d", "k", "Approach", "User Time (s)", "System Time (s)", "Elapsed Time (s)", "CPU %", "RSS (KB)"))
        f.write("-" * 100 + "\n")
        
        for d in sorted(set(d for d, _, _ in grouped_data.keys())):
            for k in sorted(set(k for _, k, _ in grouped_data.keys())):
                for approach in ['efficient', 'ingenuous']:
                    key = (d, k, approach)
                    if key in grouped_data and len(grouped_data[key]) > 0:
                        user_stats = calculate_statistics(grouped_data[key], 'user_time')
                        sys_stats = calculate_statistics(grouped_data[key], 'system_time')
                        elapsed_stats = calculate_statistics(grouped_data[key], 'elapsed_time')
                        cpu_stats = calculate_statistics(grouped_data[key], 'cpu_percent')
                        rss_stats = calculate_statistics(grouped_data[key], 'max_resident_set_size')
                        
                        f.write("{:<8} {:<8} {:<12} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.1f} {:<15}\n".format(
                            d, k, approach,
                            user_stats['mean'],
                            sys_stats['mean'],
                            elapsed_stats['mean'],
                            cpu_stats['mean'],
                            int(rss_stats['mean'])))
            f.write("-" * 100 + "\n")
        
        # Add section for context switches
        f.write("\n\nContext Switches Statistics\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("{:<8} {:<8} {:<12} {:<15} {:<15}\n".format(
            "d", "k", "Approach", "Voluntary", "Involuntary"))
        f.write("-" * 60 + "\n")
        
        for d in sorted(set(d for d, _, _ in grouped_data.keys())):
            for k in sorted(set(k for _, k, _ in grouped_data.keys())):
                for approach in ['efficient', 'ingenuous']:
                    key = (d, k, approach)
                    if key in grouped_data and len(grouped_data[key]) > 0:
                        vol_stats = calculate_statistics(grouped_data[key], 'voluntary_ctx_switches')
                        invol_stats = calculate_statistics(grouped_data[key], 'involuntary_ctx_switches')
                        
                        f.write("{:<8} {:<8} {:<12} {:<15} {:<15}\n".format(
                            d, k, approach,
                            int(vol_stats['mean']),
                            int(invol_stats['mean'])))
            f.write("-" * 60 + "\n")

def generate_html_report(output_dir):
    """Generate an HTML report that includes all the generated plots."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Time Performance Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            h1, h2, h3 { color: #333; }
            .section { margin-bottom: 40px; }
            .plot-container { margin: 20px 0; text-align: center; }
            .plot-container img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }
            .plot-caption { font-style: italic; color: #666; margin-top: 8px; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .summary { background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Time Performance Analysis Report</h1>
        
        <div class="section">
            <h2>Overview</h2>
            <p>This report presents the analysis of time performance metrics for different configurations of track sizes (d), 
            cyclist counts (k), and implementation approaches (efficient vs. ingenuous).</p>
        </div>
        
        <div class="section">
            <h2>User Time Analysis</h2>
            <div class="plot-container">
                <img src="user_time_by_track_size.png" alt="User Time by Track Size">
                <p class="plot-caption">Comparison of user time across different track sizes</p>
            </div>
            
            <div class="plot-container">
                <img src="user_time_by_cyclists.png" alt="User Time by Cyclists">
                <p class="plot-caption">Comparison of user time across different cyclist counts</p>
            </div>
            
            <div class="plot-container">
                <img src="user_time_by_approach.png" alt="User Time by Approach">
                <p class="plot-caption">Comparison of user time between efficient and ingenuous approaches</p>
            </div>
        </div>
        
        <div class="section">
            <h2>System Time Analysis</h2>
            <div class="plot-container">
                <img src="system_time_by_track_size.png" alt="System Time by Track Size">
                <p class="plot-caption">Comparison of system time across different track sizes</p>
            </div>
            
            <div class="plot-container">
                <img src="system_time_by_cyclists.png" alt="System Time by Cyclists">
                <p class="plot-caption">Comparison of system time across different cyclist counts</p>
            </div>
            
            <div class="plot-container">
                <img src="system_time_by_approach.png" alt="System Time by Approach">
                <p class="plot-caption">Comparison of system time between efficient and ingenuous approaches</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Elapsed Time Analysis</h2>
            <div class="plot-container">
                <img src="elapsed_time_by_track_size.png" alt="Elapsed Time by Track Size">
                <p class="plot-caption">Comparison of elapsed time across different track sizes</p>
            </div>
            
            <div class="plot-container">
                <img src="elapsed_time_by_cyclists.png" alt="Elapsed Time by Cyclists">
                <p class="plot-caption">Comparison of elapsed time across different cyclist counts</p>
            </div>
            
            <div class="plot-container">
                <img src="elapsed_time_by_approach.png" alt="Elapsed Time by Approach">
                <p class="plot-caption">Comparison of elapsed time between efficient and ingenuous approaches</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Context Switches Analysis</h2>
            <div class="plot-container">
                <img src="context_switches.png" alt="Context Switches">
                <p class="plot-caption">Comparison of voluntary vs. involuntary context switches</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Conclusions</h2>
            <div class="summary">
                <p>This section automatically highlights key findings from the performance analysis:</p>
                <ul>
                    <li>Comparison between approaches: Which approach (efficient or ingenuous) performs better?</li>
                    <li>Scaling behavior: How does performance scale with track size and cyclist count?</li>
                    <li>Resource usage patterns: Any significant observations about CPU usage or context switches?</li>
                </ul>
                <p><em>Note: Review the complete time_summary_statistics.txt file for detailed statistics.</em></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, 'time_analysis_report.html'), 'w') as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description='Analyze time command output files for program execution.')
    parser.add_argument('--input', '-i', required=True, help='Input directory containing time output files')
    parser.add_argument('--output', '-o', default='time_analysis', help='Output directory for graphs and analysis')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Get list of files
    file_list = glob.glob(os.path.join(args.input, '*.txt'))
    
    if not file_list:
        print(f"No time output files found in: {args.input}")
        return
    
    print(f"Found {len(file_list)} time output files")
    
    # Parse all files
    data_list = []
    for file in file_list:
        print(f"Processing: {os.path.basename(file)}")
        data_list.append(TimeData(file))
    
    # Group data by parameters
    grouped_data = group_data_by_parameters(data_list)
    print(f"Grouped into {len(grouped_data)} parameter combinations")
    
    # Generate plots for different metrics
    metrics = [
        ('User Time', 'user_time', 'User Time (seconds)'),
        ('System Time', 'system_time', 'System Time (seconds)'),
        ('Elapsed Time', 'elapsed_time', 'Elapsed Time (seconds)'),
        ('CPU Usage', 'cpu_percent', 'CPU Usage (%)')
    ]
    
    for metric_name, metric, y_label in metrics:
        plot_time_comparison_by_track_size(grouped_data, args.output, metric_name, metric, y_label)
        plot_time_comparison_by_cyclists(grouped_data, args.output, metric_name, metric, y_label)
        plot_time_comparison_by_approach(grouped_data, args.output, metric_name, metric, y_label)
    
    # Plot context switches
    plot_context_switches(grouped_data, args.output)
    
    # Generate summary table
    generate_summary_table(grouped_data, args.output)
    
    # Generate HTML report
    generate_html_report(args.output)
    
    print(f"Analysis complete. Results saved to: {args.output}")
    print(f"Open {os.path.join(args.output, 'time_analysis_report.html')} to view the report")

if __name__ == "__main__":
    main() 