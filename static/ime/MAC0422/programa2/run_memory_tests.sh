#!/bin/bash

# Define the parameter matrices
K_VALUES=(10 25 50)
D_VALUES=(100 250 500)
APPROACHES=("i" "e")
NUM_ITERATIONS=30  # Number of iterations for statistical significance

# Create directory for massif output files if it doesn't exist
mkdir -p massif_results

# Run all combinations with valgrind massif
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
                OUTPUT_FILE="massif_results/massif_d${d}_k${k}_${approach}_iter${iteration}.out"
                
                # Check if the output file already exists
                if [ -f "$OUTPUT_FILE" ]; then
                    echo "Skipping d=$d, k=$k, approach=$approach (iteration $iteration) - output file already exists"
                    continue
                fi
                
                echo "Running with d=$d, k=$k, approach=$approach (iteration $iteration of $NUM_ITERATIONS)"
                
                # Run with valgrind massif
                valgrind --tool=massif --massif-out-file="$OUTPUT_FILE" ./ep2 "$d" "$k" "$approach"
                
                echo "Completed iteration $iteration. Massif output saved to $OUTPUT_FILE"

            done
            
            echo "Completed all iterations for d=$d, k=$k, approach=$approach"
            echo "----------------------------------------"
        done
    done
done

echo "All tests completed. Results are in the massif_results directory."
echo "You can use ms_print to view the results, e.g.:"
echo "ms_print massif_results/massif_d100_k10_i_iter1.out"