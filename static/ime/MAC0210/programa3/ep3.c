#include "ep3.h"

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <part_number>\n", argv[0]);
        return 1;
    }

    int part_number = atoi(argv[1]);

    if (part_number < 1 || part_number > 2) {
        printf("Invalid part number\n");
        return 1;
    }

    switch (part_number) {
        case 1:
            part_1();
            break;
        case 2:
            part_2();
            break;
        default:
            printf("Invalid part number\n");
            return 1;
    }
}

double* lagrange_interpolation(int n, DataPoint *data) {
    // Allocate memory for result coefficients
    double *result = (double*)malloc(n * sizeof(double));
    if (result == NULL) {
        return NULL; // Memory allocation failed
    }
    
    // Initialize result array to zeros
    for (int i = 0; i < n; i++) {
        result[i] = 0.0;
    }
    
    // For each data point, compute its contribution to the polynomial
    for (int i = 0; i < n; i++) {
        // Compute the Lagrange basis polynomial L_i(x)
        // Start with the constant term y[i]
        double temp[n];
        for (int j = 0; j < n; j++) {
            temp[j] = 0.0;
        }
        temp[0] = data[i].y;
        
        // Multiply by each factor (x - x_j) / (x_i - x_j) for j != i
        for (int j = 0; j < n; j++) {
            if (i != j) {
                double factor = 1.0 / (data[i].x - data[j].x);
                
                // Multiply temp polynomial by (x - x[j]) * factor
                double new_temp[n];
                for (int k = 0; k < n; k++) {
                    new_temp[k] = 0.0;
                }
                
                // Multiply by x * factor
                for (int k = 0; k < n - 1; k++) {
                    new_temp[k + 1] += temp[k] * factor;
                }
                
                // Multiply by -x[j] * factor
                for (int k = 0; k < n; k++) {
                    new_temp[k] += temp[k] * (-data[j].x) * factor;
                }
                
                // Copy back to temp
                for (int k = 0; k < n; k++) {
                    temp[k] = new_temp[k];
                }
            }
        }
        
        // Add this basis polynomial contribution to the result
        for (int k = 0; k < n; k++) {
            result[k] += temp[k];
        }
    }
    
    return result;
}

double evaluate_polynomial(double *coefficients, int n, double x) {
    double result = 0.0;
    double x_power = 1.0;
    
    for (int i = 0; i < n; i++) {
        result += coefficients[i] * x_power;
        x_power *= x;
    }
    
    return result;
}

double trapezoid_rule(double *coefficients, int n, double a, double b, int num_intervals) {
    double h = (b - a) / num_intervals;
    double sum = 0.0;
    
    // First point
    sum += evaluate_polynomial(coefficients, n, a);
    
    // Middle points
    for (int i = 1; i < num_intervals; i++) {
        double x = a + i * h;
        sum += 2.0 * evaluate_polynomial(coefficients, n, x);
    }
    
    // Last point
    sum += evaluate_polynomial(coefficients, n, b);
    
    return (h / 2.0) * sum;
}

double simpson_rule(double *coefficients, int n, double a, double b, int num_intervals) {
    // Ensure num_intervals is even
    if (num_intervals % 2 != 0) {
        num_intervals++; // Make it even
    }
    
    double h = (b - a) / num_intervals;
    double sum = 0.0;
    
    // First point
    sum += evaluate_polynomial(coefficients, n, a);
    
    // Middle points
    for (int i = 1; i < num_intervals; i++) {
        double x = a + i * h;
        double weight = (i % 2 == 0) ? 2.0 : 4.0;
        sum += weight * evaluate_polynomial(coefficients, n, x);
    }
    
    // Last point
    sum += evaluate_polynomial(coefficients, n, b);
    
    return (h / 3.0) * sum;
}

void part_1(void) {
    DataPoint data[7];
    int n = 7;

    data[0].x = 0;
    data[0].y = 0;

    data[1].x = 5;
    data[1].y = 1.5297;
    
    data[2].x = 10;
    data[2].y = 9.5120;

    data[3].x = 15;
    data[3].y = 8.7025;

    data[4].x = 20;
    data[4].y = 2.8087;

    data[5].x = 25;
    data[5].y = 1.0881;

    data[6].x = 30;
    data[6].y = 0.3537;

    double *coefficients = lagrange_interpolation(n, data);
    
    if (coefficients != NULL) {
        printf("Lagrange interpolation coefficients:\n");
        for (int i = 0; i < n; i++) {
            printf("x^%d: %.6f\n", i, coefficients[i]);
        }
        
        // Numerical integration of the interpolated polynomial
        double a = data[0].x;  // Lower limit of integration
        double b = data[n-1].x; // Upper limit of integration (from x=0 to x=30)
        int num_intervals = 1000; // Number of intervals for integration
        
        printf("\nNumerical Integration Results:\n");
        printf("Integration limits: [%.1f, %.1f]\n", a, b);
        printf("Number of intervals: %d\n", num_intervals);
        
        // Trapezoidal rule
        double trapezoid_result = trapezoid_rule(coefficients, n, a, b, num_intervals);
        printf("Trapezoidal rule result: %.6f\n", trapezoid_result);
        
        // Simpson's rule
        double simpson_result = simpson_rule(coefficients, n, a, b, num_intervals);
        printf("Simpson's rule result: %.6f\n", simpson_result);
        
        // Calculate the difference between methods
        double difference = fabs(simpson_result - trapezoid_result);
        printf("Absolute difference between methods: %.6f\n", difference);
        
        // Free allocated memory
        free(coefficients);
    } else {
        printf("Error: Memory allocation failed\n");
    }
}

void part_2(void) {
    return;
}
