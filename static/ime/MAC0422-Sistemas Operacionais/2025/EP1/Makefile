CC = gcc
CFLAGS = -Wall -g
LDFLAGS = -lreadline -pthread

# Source files for uspsh
USPSH_SRCS = uspsh.c
USPSH_OBJS = $(USPSH_SRCS:.c=.o)
USPSH_TARGET = uspsh

# Source files for ep1
EP1_SRCS = ep1.c
EP1_OBJS = $(EP1_SRCS:.c=.o)
EP1_TARGET = ep1

# Default target
all: $(USPSH_TARGET) $(EP1_TARGET)

# Build uspsh
$(USPSH_TARGET): $(USPSH_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Build ep1
$(EP1_TARGET): $(EP1_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $<

# Clean build artifacts
clean:
	rm -f $(USPSH_TARGET) $(EP1_TARGET) $(USPSH_OBJS) $(EP1_OBJS)

# Run uspsh
run-uspsh: $(USPSH_TARGET)
	./$(USPSH_TARGET)

# Run ep1
run-ep1: $(EP1_TARGET)
	./$(EP1_TARGET)

# Run both programs
run: run-uspsh run-ep1

# Help target
help:
	@echo "Available targets:"
	@echo "  make              - Build both programs"
	@echo "  make uspsh        - Build only the shell"
	@echo "  make ep1          - Build only ep1"
	@echo "  make clean        - Remove all build artifacts"
	@echo "  make run-uspsh    - Run the shell"
	@echo "  make run-ep1      - Run ep1"
	@echo "  make run          - Run both programs"
	@echo "  make help         - Show this help message"

.PHONY: all clean run run-uspsh run-ep1 help
