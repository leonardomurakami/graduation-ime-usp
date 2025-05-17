CC=gcc
CFLAGS=-Wall -Wextra -g -pthread
LDLIBS=-lm -pthread

all: ep2

ep2: ep2.c ep2.h
	$(CC) $(CFLAGS) -o ep2 ep2.c $(LDLIBS)

clean:
	rm -f ep2 *.o

.PHONY: all clean 