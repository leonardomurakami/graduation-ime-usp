import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def get_preemption_data(directory):
    preemptions = []
    for filename in os.listdir(directory):
        if filename.startswith('output_') and filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r') as f:
                lines = f.readlines()
                if lines:
                    try:
                        preemption = int(lines[-1].strip())
                        preemptions.append(preemption)
                    except (ValueError, IndexError):
                        print(f"Warning: Invalid data in {filename}")
                        continue
    if not preemptions:
        print(f"Warning: No valid data found in {directory}")
        return [0]  # Return a default value to prevent errors
    if len(preemptions) != 30:
        print(f"Warning: Found {len(preemptions)} measurements in {directory}, expected 30")
    return preemptions[:30]  # Ensure we use exactly 30 measurements

def calculate_statistics(data):
    if len(data) < 2:
        return 0, 0, (0, 0)  # Return default values for insufficient data
    mean = np.mean(data)
    std = np.std(data, ddof=1)  # Using ddof=1 for sample standard deviation
    n = len(data)
    # Calculate 95% confidence interval
    try:
        ci = stats.t.interval(0.95, n-1, loc=mean, scale=std/np.sqrt(n))
    except (ValueError, RuntimeWarning):
        ci = (mean - 2*std, mean + 2*std)  # Fallback to approximate CI
    return mean, std, ci

# Directory paths
base_dir = 'inesperado/4-threads'
algorithms = ['fcfs', 'srtn', 'priority']

# Collect data for each algorithm
data = {}
for algo in algorithms:
    algo_dir = os.path.join(base_dir, algo)
    data[algo] = get_preemption_data(algo_dir)

# Calculate statistics
stats_data = {}
for algo in algorithms:
    stats_data[algo] = calculate_statistics(data[algo])

# Create the plot
plt.figure(figsize=(12, 8))
x = np.arange(len(algorithms))
width = 0.6

# Plot bars
means = [stats_data[algo][0] for algo in algorithms]
stds = [stats_data[algo][1] for algo in algorithms]
cis = [stats_data[algo][2] for algo in algorithms]

# Calculate error bars for confidence intervals
yerr = np.array([(mean - ci[0], ci[1] - mean) for mean, ci in zip(means, cis)]).T

bars = plt.bar(x, means, width, yerr=yerr, capsize=5, 
        color=['#1f77b4', '#ff7f0e', '#2ca02c'])

# Add labels and title
plt.xlabel('Scheduling Algorithm')
plt.ylabel('Number of Preemptions')
plt.title('Preemption Statistics by Scheduling Algorithm (95% CI)\nBased on 30 measurements per algorithm')
plt.xticks(x, [algo.upper() for algo in algorithms])

# Add statistics text above each bar
for i, (mean, std, ci) in enumerate(zip(means, stds, cis)):
    # Position the text above the bar
    y_pos = mean + yerr[1][i] + 0.5
    
    # Add mean value
    plt.text(i, y_pos, f'Mean: {mean:.1f}', ha='center', fontsize=9)
    
    # Add standard deviation
    plt.text(i, y_pos + 0.8, f'Std Dev: {std:.1f}', ha='center', fontsize=9)
    
    # Add confidence interval
    plt.text(i, y_pos + 1.6, f'95% CI: ({ci[0]:.1f}, {ci[1]:.1f})', 
             ha='center', fontsize=9)

# Calculate y-axis limits safely
max_y = max(means) + max(yerr[1]) + 3
if not np.isnan(max_y) and not np.isinf(max_y):
    plt.ylim(0, max_y)
else:
    plt.ylim(0, max(means) * 1.5)  # Fallback if there are NaN/Inf values

plt.tight_layout()
plt.savefig('preemption_statistics.png', dpi=300, bbox_inches='tight')
plt.close()

# Print statistics
print("\nPreemption Statistics:")
print("Algorithm\tMean\tStd Dev\t95% CI\t\tMeasurements")
for algo in algorithms:
    mean, std, ci = stats_data[algo]
    n_measurements = len(data[algo])
    print(f"{algo.upper()}\t\t{mean:.2f}\t{std:.2f}\t({ci[0]:.2f}, {ci[1]:.2f})\t{n_measurements}")
