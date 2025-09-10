JAVA_FILES = Programa1.java Programa2.java Programa3.java Programa4.java
CLASS_FILES = $(JAVA_FILES:.java=.class)

all: $(CLASS_FILES)

programa1: Programa1.class

programa2: Programa2.class

programa3: Programa3.class

programa4: Programa4.class


%.class: %.java
	@javac $<

test1: Programa1.class
	@java Programa1 tabela_simbolos.txt texto.txt > out1

test2: Programa2.class
	@java Programa2 --output-compressed out1 > out2

test3: Programa3.class
	@java Programa3 out2 compressed > out3

test4: Programa4.class
	@java Programa4 out3 tabela_simbolos.txt > out4

test: $(CLASS_FILES)
	@java Programa1 tabela_simbolos.txt texto.txt > out1
	@java Programa2 --output-compressed out1 > out2
	@java Programa3 out2 compressed > out3
	@java Programa4 out3 tabela_simbolos.txt > out4

clean:
	rm -f *.class saida_temp.txt
	rm -f out1 out2 out3 out4 compressed

.PHONY: all test1 test2 test3 test_pipeline clean 