TARGET = mini_ep4
SOURCES = mini_ep4.c
CFLAGS = -Wall -g 

# Regra padrão para compilar com gprof
all: $(TARGET)_gprof

# Regra para compilar com gprof
$(TARGET)_gprof: $(SOURCES)
	gcc -pg $(CFLAGS) -o $@ $^

# Regra para compilar para usar com perf
$(TARGET)_perf: $(SOURCES)
	gcc $(CFLAGS) -o $@ $^

clean:
	rm -f $(TARGET)_gprof $(TARGET)_perf gmon.out