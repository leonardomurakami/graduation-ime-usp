# Java compiler
JC = javac

# Java runtime
JAVA = java

# Source files
SRCS = $(wildcard *.java)

# Class files
CLASSES = $(SRCS:.java=.class)

# Default target
all: $(CLASSES)

# Compile Java files
%.class: %.java
	$(JC) $(SRCS)

# Run the program
run: $(CLASSES)
	$(JAVA) Main

# Clean generated files
clean:
	rm -f *.class

.PHONY: all run clean test-gen

