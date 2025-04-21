import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def get_deadline_data(directory):
    deadline_met_percentages = []
    for filename in os.listdir(directory):
        if filename.startswith('output_') and filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:  # Ensure we have at least one process line
                    try:
                        # Skip the last line (preemption count) and count deadline successes
                        process_lines = [line.strip() for line in lines[:-1] if line.strip()]
                        deadline_met = sum(1 for line in process_lines if line.split()[-1] == '1')
                        total_processes = len(process_lines)
                        if total_processes > 0:
                            percentage = (deadline_met / total_processes) * 100
                            deadline_met_percentages.append(percentage)
                    except (ValueError, IndexError):
                        print(f"Warning: Invalid data in {filename}")
                        continue
    if not deadline_met_percentages:
        print(f"Warning: No valid data found in {directory}")
        return [0]  # Return a default value to prevent errors
    if len(deadline_met_percentages) != 30:
        print(f"Warning: Found {len(deadline_met_percentages)} measurements in {directory}, expected 30")
    return deadline_met_percentages[:30]  # Ensure we use exactly 30 measurements

def calculate_statistics(data):
    if len(data) < 2:
        return 0, 0, (0, 0)  # Return default values for insufficient data
    
    # Convert to numpy array for better handling
    data = np.array(data)
    
    # Handle edge cases where all values are the same
    if np.all(data == data[0]):
        return data[0], 0, (data[0], data[0])
    
    mean = np.mean(data)
    std = np.std(data, ddof=1)  # Using ddof=1 for sample standard deviation
    n = len(data)
    
    # Calculate 95% confidence interval with more robust error handling
    try:
        if n > 1:
            ci = stats.t.interval(0.95, n-1, loc=mean, scale=std/np.sqrt(n))
        else:
            ci = (mean, mean)
    except (ValueError, RuntimeWarning):
        ci = (mean - 2*std, mean + 2*std)  # Fallback to approximate CI
    
    # Ensure CI doesn't go beyond 0-100% range
    ci = (max(0, ci[0]), min(100, ci[1]))
    
    return mean, std, ci

# Directory paths
base_dir = 'inesperado/6-threads'
algorithms = ['fcfs', 'srtn', 'priority']

# Collect data for each algorithm
data = {}
for algo in algorithms:
    algo_dir = os.path.join(base_dir, algo)
    data[algo] = get_deadline_data(algo_dir)

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
plt.xlabel('Scheduling Algorithm', fontsize=12)
plt.ylabel('Percentage of Deadlines Met', fontsize=12)
plt.title('Deadline Compliance by Scheduling Algorithm (95% CI)\nBased on 30 measurements per algorithm', fontsize=14, pad=20)
plt.xticks(x, [algo.upper() for algo in algorithms], fontsize=12)

# Add statistics text inside each bar
for i, (mean, std, ci) in enumerate(zip(means, stds, cis)):
    # Position the text inside the bar with proper spacing
    text_spacing = mean / 4  # Dynamic spacing based on bar height
    
    # Add mean value at the top of the bar
    plt.text(i, mean - text_spacing, f'Mean: {mean:.1f}%', 
             ha='center', fontsize=10, va='top')
    
    # Add standard deviation in the middle
    plt.text(i, mean/2, f'Std Dev: {std:.1f}%', 
             ha='center', fontsize=10, va='center')
    
    # Add confidence interval near the bottom
    plt.text(i, text_spacing, f'95% CI: ({ci[0]:.1f}%, {ci[1]:.1f}%)', 
             ha='center', fontsize=10, va='bottom')

# Calculate y-axis limits safely
max_y = max(means) + max(yerr[1]) + 2
if not np.isnan(max_y) and not np.isinf(max_y):
    plt.ylim(0, min(max_y, 100))  # Cap at 100% since we're dealing with percentages
else:
    plt.ylim(0, 100)  # Fallback if there are NaN/Inf values

plt.tight_layout()
plt.savefig('deadline_compliance_statistics.png', dpi=300, bbox_inches='tight')
plt.close()

# Print statistics with improved formatting
print("\nDeadline Compliance Statistics:")
print("-" * 80)
print(f"{'Algorithm':<12} {'Mean':<8} {'Std Dev':<8} {'95% CI':<25} {'Measurements':<12}")
print("-" * 80)
for algo in algorithms:
    mean, std, ci = stats_data[algo]
    n_measurements = len(data[algo])
    print(f"{algo.upper():<12} {mean:>7.2f}% {std:>7.2f}% ({ci[0]:>6.2f}%, {ci[1]:>6.2f}%) {n_measurements:>12}")
print("-" * 80) 