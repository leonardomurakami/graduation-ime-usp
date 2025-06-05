CC=gcc
CFLAGS=-Wall -Wextra -g -pthread
LDLIBS=-lm -pthread

# Default target
all: ep2

# Help command
help:
	@echo "Available commands:"
	@echo "  make          - Build the program"
	@echo "  make clean    - Remove generated files"
	@echo "  make run      - Run with increased thread limit"
	@echo "  make help     - Display this help message"
	@echo
	@echo "Usage examples:"
	@echo "  make run 2500 12500 e        - Run with track size 2500, 12500 cyclists, efficient approach"
	@echo "  make run 2000 5000 i -debug  - Run with debug mode and naive approach"

ep2: ep2.c ep2.h
	$(CC) $(CFLAGS) -o ep2 ep2.c $(LDLIBS)

# Run with arguments: make run <d> <k> <approach>
run:
	@if [ "$(filter-out $@,$(MAKECMDGOALS))" = "" ]; then \
		echo "Usage: make run <d> <k> <approach> [options]"; \
	else \
		ulimit -n 16384 && ./ep2 $(filter-out $@,$(MAKECMDGOALS)); \
	fi

clean:
	rm -f ep2 *.o

.PHONY: all clean run help

%:
	@: 