#ifndef EP3_H
#define EP3_H

#include <stdio.h> // For FILE*
#include <stdlib.h> // For exit, atoi
#include <string.h> // For strcmp, strlen, strncpy, strcspn
#include <limits.h> // For INT_MAX

// Constants for memory and PGM file structure
#define TOTAL_MEMORY_UNITS 65536       // 
#define PGM_WIDTH 256                  // 
#define PGM_HEIGHT 256                 // 
#define PGM_MAX_VAL 255                // 

// PGM header: "P2\n256 256\n255\n"
// "P2\n" (3 bytes)
// "256 256\n" (8 bytes)
// "255\n" (4 bytes)
#define PGM_HEADER_SIZE 15             // 

#define UNITS_PER_FILE_LINE 16         // 
// Each line of pixel data: 16 units * 3 chars/unit + 15 spaces + 1 newline = 48 + 15 + 1 = 64 bytes 
#define BYTES_PER_FILE_DATA_LINE 64

#define STATUS_USED 0                  // Represents a black pixel, unit in use 
#define STATUS_FREE 255                // Represents a white pixel, unit available 

#define TRACE_LINE_MAX_LEN 256
#define MAX_FAILED_REQS 2001 // Max 2000 lines in trace + 1 for safety 

// Function Prototypes

/**
 * @brief Copies the content of the input PGM file to the output PGM file.
 * This operation is allowed to use memory without the EP's usual restrictions. 
 * @param input_filename Path to the input PGM file.
 * @param output_filename Path to the output PGM file to be created.
 */
void copy_pgm_file(const char *input_filename, const char *output_filename);

/**
 * @brief Calculates the file offset for a given memory unit index.
 * The offset points to the start of the 3-character representation of the unit's value.
 * @param unit_index The 0-based index of the memory unit (0 to TOTAL_MEMORY_UNITS - 1).
 * @return The file offset from the beginning of the file.
 */
long get_unit_file_offset(int unit_index);

/**
 * @brief Reads the status of a memory unit directly from the PGM file.
 * @param fp File pointer to the PGM file, opened in "r+b" mode.
 * @param unit_index The 0-based index of the memory unit.
 * @return The status of the unit (STATUS_FREE or STATUS_USED), or -1 on error.
 */
int read_unit_status(FILE *fp, int unit_index);

/**
 * @brief Writes the status of a memory unit directly to the PGM file.
 * Writes "  0" for STATUS_USED or "255" for STATUS_FREE. 
 * @param fp File pointer to the PGM file, opened in "r+b" mode.
 * @param unit_index The 0-based index of the memory unit.
 * @param status The new status to write (STATUS_FREE or STATUS_USED).
 */
void write_unit_status(FILE *fp, int unit_index, int status);

/**
 * @brief Allocates a block of memory units by marking them as used in the PGM file.
 * @param fp File pointer to the PGM file.
 * @param start_index The starting unit index of the block to allocate.
 * @param size The number of units to allocate.
 */
void allocate_memory_units(FILE *fp, int start_index, int size);

/**
 * @brief Implements the First Fit memory allocation algorithm.
 * Finds the first free block large enough for the requested size.
 * @param fp File pointer to the PGM file.
 * @param size_needed The number of contiguous memory units required.
 * @param total_units Total number of units in memory.
 * @return The starting index of the allocated block, or -1 if no suitable block is found.
 */
int find_first_fit(FILE *fp, int size_needed, int total_units);

/**
 * @brief Implements the Next Fit memory allocation algorithm.
 * Starts searching from the position after the last allocation.
 * @param fp File pointer to the PGM file.
 * @param size_needed The number of contiguous memory units required.
 * @param total_units Total number of units in memory.
 * @param last_pos Pointer to an integer storing the last allocation position (updated by this function).
 * @return The starting index of the allocated block, or -1 if no suitable block is found.
 */
int find_next_fit(FILE *fp, int size_needed, int total_units, int *last_pos);

/**
 * @brief Implements the Best Fit memory allocation algorithm.
 * Finds the smallest free block that is large enough for the requested size.
 * @param fp File pointer to the PGM file.
 * @param size_needed The number of contiguous memory units required.
 * @param total_units Total number of units in memory.
 * @return The starting index of the allocated block, or -1 if no suitable block is found.
 */
int find_best_fit(FILE *fp, int size_needed, int total_units);

/**
 * @brief Implements the Worst Fit memory allocation algorithm.
 * Finds the largest free block that is large enough for the requested size.
 * @param fp File pointer to the PGM file.
 * @param size_needed The number of contiguous memory units required.
 * @param total_units Total number of units in memory.
 * @return The starting index of the allocated block, or -1 if no suitable block is found.
 */
int find_worst_fit(FILE *fp, int size_needed, int total_units);

/**
 * @brief Compacts the memory in the PGM file.
 * All used blocks are moved to the beginning, and all free blocks to the end. 
 * This is done by reading and writing unit statuses directly in the file.
 * @param fp File pointer to the PGM file.
 * @param total_units Total number of units in memory.
 */
void compact_memory(FILE *fp, int total_units);

#endif // EP3_H