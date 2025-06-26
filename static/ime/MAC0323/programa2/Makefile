JAVA_FILES = Programa1.java Programa2.java Programa3.java
CLASS_FILES = $(JAVA_FILES:.java=.class)

all: $(CLASS_FILES)

%.class: %.java
	@javac $<

test1: Programa1.class
	@java Programa1 tabela_simbolos.txt teste.txt > out1

test2: Programa2.class
	@java Programa2 out1 > out2

test3: Programa3.class
	@java Programa3 out2 binario.txt > out3

test: $(CLASS_FILES)
	@java Programa1 tabela_simbolos.txt teste.txt > out1
	@java Programa2 out1 > out2
	@java Programa3 out2 binario.txt > out3

test_pipeline: Programa1.class Programa2.class
	java Programa1 tabela_simbolos.txt teste.txt > saida_temp.txt
	java Programa2 saida_temp.txt
	rm -f saida_temp.txt

clean:
	rm -f *.class saida_temp.txt

.PHONY: all test1 test2 test3 test_pipeline clean 