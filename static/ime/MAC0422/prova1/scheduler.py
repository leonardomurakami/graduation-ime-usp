class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        
    def __repr__(self):
        return f"{self.name}(arr:{self.arrival}, burst:{self.burst}, rem:{self.remaining})"

def fcfs(processes):
    # Create deep copies to avoid modifying original processes
    procs = [Process(p.name, p.arrival, p.burst) for p in processes]
    timeline = []
    current_time = 0
    for process in sorted(procs, key=lambda x: x.arrival):
        if current_time < process.arrival:
            timeline.extend(['Idle'] * (process.arrival - current_time))
            current_time = process.arrival
        timeline.extend([process.name] * process.burst)
        current_time += process.burst
    return timeline

def sjf(processes):
    # Create deep copies to avoid modifying original processes
    procs = [Process(p.name, p.arrival, p.burst) for p in processes]
    timeline = []
    current_time = 0
    procs = sorted(procs, key=lambda x: (x.arrival, x.burst))
    while procs:
        available_processes = [p for p in procs if p.arrival <= current_time]
        if not available_processes:
            timeline.append('Idle')
            current_time += 1
            continue
        process = min(available_processes, key=lambda x: x.burst)
        procs.remove(process)
        timeline.extend([process.name] * process.burst)
        current_time += process.burst
    return timeline

def srtn(processes):
    # Create deep copies to avoid modifying original processes
    procs = [Process(p.name, p.arrival, p.burst) for p in processes]
    timeline = []
    current_time = 0
    ready_queue = []
    remaining_processes = sorted(procs, key=lambda x: x.arrival)
    
    while ready_queue or remaining_processes:
        # Move arriving processes to ready queue
        while remaining_processes and remaining_processes[0].arrival <= current_time:
            ready_queue.append(remaining_processes.pop(0))
            
        if not ready_queue:
            # If no process is ready, advance time to next arrival
            timeline.append('Idle')
            current_time = remaining_processes[0].arrival
            continue
            
        # Select process with shortest remaining time
        ready_queue.sort(key=lambda x: x.remaining)
        current_process = ready_queue[0]
        
        # Determine how long to run current process
        run_time = 1  # Default to 1 time unit
        
        # Check if a new process will arrive
        if remaining_processes:
            next_arrival = remaining_processes[0].arrival
            if next_arrival > current_time:
                # Run until next process arrives or current process completes
                run_time = min(current_process.remaining, next_arrival - current_time)
        else:
            # No more arrivals, run until completion
            run_time = current_process.remaining
            
        # Execute process for calculated time
        timeline.extend([current_process.name] * run_time)
        current_time += run_time
        current_process.remaining -= run_time
        
        # If process is complete, remove from ready queue
        if current_process.remaining == 0:
            ready_queue.remove(current_process)
            
    return timeline

def round_robin(processes, quantum):
    # Create deep copies to avoid modifying original processes
    procs = [Process(p.name, p.arrival, p.burst) for p in processes]
    timeline = []
    current_time = 0
    queue = []
    remaining_processes = sorted(procs, key=lambda x: x.arrival)
    
    while queue or remaining_processes:
        # Move arriving processes to ready queue
        while remaining_processes and remaining_processes[0].arrival <= current_time:
            queue.append(remaining_processes.pop(0))
            
        if not queue:
            # If no process is ready, advance time to next arrival
            timeline.append('Idle')
            current_time = remaining_processes[0].arrival
            continue
            
        process = queue.pop(0)
        execution_time = min(process.remaining, quantum)
        timeline.extend([process.name] * execution_time)
        current_time += execution_time
        process.remaining -= execution_time
        
        # Move any processes that arrived during execution to ready queue
        while remaining_processes and remaining_processes[0].arrival <= current_time:
            queue.append(remaining_processes.pop(0))
            
        if process.remaining > 0:
            queue.append(process)
            
    return timeline

def format_timeline(timeline):
    """Convert timeline to a more readable format showing process changes"""
    if not timeline:
        return "[]"
        
    formatted = []
    current = timeline[0]
    count = 1
    
    for i in range(1, len(timeline)):
        if timeline[i] == current:
            count += 1
        else:
            formatted.append(f"{current}({count})")
            current = timeline[i]
            count = 1
            
    formatted.append(f"{current}({count})")
    return "[" + ", ".join(formatted) + "]"

def calculate_metrics(processes, timeline):
    """Calculate performance metrics for the scheduling algorithm"""
    # Initialize results dictionary
    process_metrics = {p.name: {'arrival': p.arrival, 'burst': p.burst} for p in processes}
    
    # Calculate completion time for each process
    for name in process_metrics:
        # Find the last occurrence of each process in the timeline
        for i in range(len(timeline)-1, -1, -1):
            if timeline[i] == name:
                process_metrics[name]['completion'] = i + 1  # +1 because timeline is 0-indexed
                break
    
    # Calculate turnaround time (completion - arrival)
    for name, metrics in process_metrics.items():
        metrics['turnaround'] = metrics['completion'] - metrics['arrival']
    
    # Calculate waiting time (turnaround - burst)
    for name, metrics in process_metrics.items():
        metrics['waiting'] = metrics['turnaround'] - metrics['burst']
    
    # Calculate response time (first execution - arrival)
    for name, metrics in process_metrics.items():
        for i in range(len(timeline)):
            if timeline[i] == name:
                metrics['response'] = i - metrics['arrival']
                break
    
    # Calculate average metrics
    avg_turnaround = sum(m['turnaround'] for m in process_metrics.values()) / len(process_metrics)
    avg_waiting = sum(m['waiting'] for m in process_metrics.values()) / len(process_metrics)
    avg_response = sum(m['response'] for m in process_metrics.values()) / len(process_metrics)
    
    # Count context switches
    context_switches = 0
    for i in range(1, len(timeline)):
        if timeline[i] != timeline[i-1] and timeline[i] != 'Idle' and timeline[i-1] != 'Idle':
            context_switches += 1
    
    # Calculate CPU utilization (non-idle time / total time)
    cpu_utilization = ((len(timeline) - timeline.count('Idle')) / len(timeline)) * 100 if timeline else 0
    
    return {
        'processes': process_metrics,
        'avg_turnaround': avg_turnaround,
        'avg_waiting': avg_waiting,
        'avg_response': avg_response,
        'context_switches': context_switches,
        'cpu_utilization': cpu_utilization
    }

def visualize_timeline(timeline, processes):
    """
    Create a text-based visualization of the timeline
    Each process gets its own line, with '*' marking when it's running
    """
    if not timeline:
        return "No timeline to visualize"
    
    # Get unique process names excluding 'Idle'
    process_names = sorted([p.name for p in processes])
    max_name_len = max(len(name) for name in process_names)
    
    # Calculate how much of the timeline to show per line
    timeline_len = len(timeline)
    
    # Create header with time markers
    header = ' ' * (max_name_len + 2) + '0'
    for i in range(10, timeline_len + 1, 10):
        pos = i
        spaces = 9 - len(str(i - 10))
        header += ' ' * spaces + str(i)
    
    # Create a time tick row
    ticks = ' ' * (max_name_len + 2)
    for i in range(timeline_len):
        if i % 5 == 0:
            ticks += '|'
        else:
            ticks += '-'
    
    # Create visualization rows for each process
    rows = [header, ticks]
    
    # Add 'IDLE' row
    idle_row = 'IDLE' + ' ' * (max_name_len - 4 + 2)
    for t in range(timeline_len):
        if timeline[t] == 'Idle':
            idle_row += '#'
        else:
            idle_row += ' '
    rows.append(idle_row)
    
    # Add a row for each process
    for name in process_names:
        row = name + ' ' * (max_name_len - len(name) + 2)
        for t in range(timeline_len):
            if timeline[t] == name:
                row += '*'
            else:
                row += ' '
        rows.append(row)
    
    return '\n'.join(rows)

def print_algorithm_results(name, timeline, metrics, processes):
    """Print detailed results for a scheduling algorithm"""
    print(f"\n{'-'*50}")
    print(f"{name} Scheduling Algorithm Results")
    print(f"{'-'*50}")
    
    print(f"Timeline: {format_timeline(timeline)}")
    print(f"Total execution time: {len(timeline)} units")
    
    print("\nTimeline Visualization:")
    print(visualize_timeline(timeline, processes))
    
    print("\nProcess Details:")
    print(f"{'Process':<10}{'Arrival':<10}{'Burst':<10}{'Completion':<12}{'Turnaround':<12}{'Waiting':<10}{'Response':<10}")
    print(f"{'-'*70}")
    
    for name, data in sorted(metrics['processes'].items()):
        print(f"{name:<10}{data['arrival']:<10}{data['burst']:<10}{data['completion']:<12}"
              f"{data['turnaround']:<12}{data['waiting']:<10}{data['response']:<10}")
    
    print("\nPerformance Metrics:")
    print(f"Average Turnaround Time: {metrics['avg_turnaround']:.2f} units")
    print(f"Average Waiting Time: {metrics['avg_waiting']:.2f} units")
    print(f"Average Response Time: {metrics['avg_response']:.2f} units")
    print(f"Context Switches: {metrics['context_switches']}")
    print(f"CPU Utilization: {metrics['cpu_utilization']:.2f}%")

# Example usage
processes = [
    Process('P1', 0, 8),
    Process('P2', 1, 4),
    Process('P3', 2, 9),
    Process('P4', 3, 5),
]

algorithms = [
    (fcfs, "First-Come First-Served (FCFS)"),
    (sjf, "Shortest Job First (SJF)"),
    (srtn, "Shortest Remaining Time Next (SRTN)"),
    (lambda p: round_robin(p, 4), "Round Robin (quantum=4)")
]

for algorithm_fn, algorithm_name in algorithms:
    # Make a deep copy of processes for each algorithm
    proc_copy = [Process(p.name, p.arrival, p.burst) for p in processes]
    timeline = algorithm_fn(proc_copy)
    metrics = calculate_metrics(processes, timeline)
    print_algorithm_results(algorithm_name, timeline, metrics, processes)
    print()