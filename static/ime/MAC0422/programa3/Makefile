CC=gcc
CFLAGS=-Wall -Wextra

# Default target
all: ep3

# Help command
help:
	@echo "Available commands:"
	@echo "  make          - Build the program"
	@echo "  make clean    - Remove generated files"
	@echo "  make help     - Display this help message"

ep3: ep3.c ep3.h
	$(CC) $(CFLAGS) -o ep3 ep3.c

clean:
	rm -f ep3 *.o

.PHONY: all clean run help

%:
	@: 