CC=gcc
CFLAGS=-Wall -Wextra
LDFLAGS=-lm

all: run

help:
	@echo "Available commands:"
	@echo "  make          - Build the program"
	@echo "  make help     - Display this help message"
	@echo "  make ep3      - Build the program"
	@echo "  make run      - Run the program"
	@echo "  make clean    - Remove generated files"

run: ep3
	./ep3

ep3: ep3.c
	$(CC) $(CFLAGS) -o ep3 ep3.c $(LDFLAGS)

clean:
	rm -f ep3 *.o

.PHONY: all clean run help

%:
	@: 


