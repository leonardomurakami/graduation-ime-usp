CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -pedantic -g -O2
LDFLAGS = -lm
TARGET = ep3
SRCDIR = .
OBJDIR = obj
SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(SOURCES:$(SRCDIR)/%.c=$(OBJDIR)/%.o)
DEPS = $(OBJECTS:.o=.d)

.PHONY: all clean debug release run

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)

$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

$(OBJDIR):
	mkdir -p $(OBJDIR)

debug: CFLAGS += -DDEBUG -g3 -O0
debug: $(TARGET)

release: CFLAGS += -DNDEBUG -O3
release: $(TARGET)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -rf $(OBJDIR) $(TARGET)

-include $(DEPS) 