NUM = $(filter-out $@,$(MAKECMDGOALS))

run:
	@if [ -f ex$(NUM).go ]; then \
		go run ex$(NUM).go; \
	elif [ -f ex$(NUM).cpp ]; then \
		g++ -o ex$(NUM) ex$(NUM).cpp && ./ex$(NUM) && rm -f ex$(NUM); \
	else \
		echo "No ex$(NUM).go or ex$(NUM).cpp found"; \
	fi

%:
	@:
