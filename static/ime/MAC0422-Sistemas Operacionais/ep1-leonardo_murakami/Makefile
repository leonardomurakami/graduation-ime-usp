build-scheduler:
	gcc -o scheduler scheduler.c

build-ep1:
	gcc -o ep1 newsh.c scheduler.c -lreadline -pthread

build: build-scheduler build-ep1

run: build-ep1
	./ep1

clean:
	rm -f scheduler newsh ep1