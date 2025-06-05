#!/bin/bash

# Define cleanup function for handling interrupts
cleanup() {
    echo -e "\nScript interrupted by user. Exiting..."
    exit 1
}

# Set trap to catch Ctrl-C and call cleanup function
trap cleanup SIGINT

# Define the parameter matrices
K_VALUES=(10 25 50)
D_VALUES=(100 250 500)
APPROACHES=("i" "e")
NUM_ITERATIONS=30  # Number of iterations for statistical significance

# Create directory for time output files if it doesn't exist
mkdir -p time_results

# Run all combinations with time utility
for k in "${K_VALUES[@]}"; do
    for d in "${D_VALUES[@]}"; do
        for approach in "${APPROACHES[@]}"; do
            # Check if k is valid (5 <= k <= 5 × d)
            if [ "$k" -lt 5 ] || [ "$k" -gt $((5 * d)) ]; then
                echo "Skipping invalid combination: k=$k is not in range [5, 5×$d]"
                continue
            fi
            
            for iteration in $(seq 1 $NUM_ITERATIONS); do
                # Create a descriptive output filename with iteration number
                OUTPUT_FILE="time_results/time_d${d}_k${k}_${approach}_iter${iteration}.txt"
                
                # Check if the output file already exists
                if [ -f "$OUTPUT_FILE" ]; then
                    echo "Skipping d=$d, k=$k, approach=$approach (iteration $iteration) - output file already exists"
                    continue
                fi
                
                echo "Running with d=$d, k=$k, approach=$approach (iteration $iteration of $NUM_ITERATIONS)"
                
                # Run program with stdout redirected to /dev/null, and only capture time output
                /usr/bin/time -v ./ep2 "$d" "$k" "$approach" > /dev/null 2> "$OUTPUT_FILE"
                
                echo "Completed iteration $iteration. Time output saved to $OUTPUT_FILE"
            done
            
            echo "Completed all iterations for d=$d, k=$k, approach=$approach"
            echo "----------------------------------------"
        done
    done
done

echo "All tests completed. Results are in the time_results directory."
echo "You can view the results with cat, e.g.:"
echo "cat time_results/time_d100_k10_i_iter1.txt" 