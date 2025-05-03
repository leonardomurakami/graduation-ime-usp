CC = gcc
CFLAGS = -Wall -g
LDFLAGS = -lreadline -pthread

EP2_SRCS = ep2.c
EP2_OBJS = $(EP2_SRCS:.c=.o)
EP2_TARGET = ep2

all: $(EP2_TARGET)

$(EP2_TARGET): $(EP2_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f $(EP2_TARGET) $(EP2_OBJS)

run: 
	./$(EP2_TARGET)

help:
	@echo "Available targets:"
	@echo "  make              - Build program"
	@echo "  make clean        - Remove all build artifacts"
	@echo "  make run          - Run the ep2"
	@echo "  make help         - Show this help message"

.PHONY: all clean run help
