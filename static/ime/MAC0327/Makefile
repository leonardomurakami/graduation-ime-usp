ARGS = $(filter-out $@,$(MAKECMDGOALS))
NUM = $(word 1,$(ARGS))
TEMPLATE = $(word 1,$(ARGS))
EXERCISE = $(word 2,$(ARGS))

run:
	@LNUM=$$(echo $(NUM) | grep -o '^[0-9]\+'); \
	if [ -f lista$$LNUM/ex$(NUM).go ]; then \
		go run lista$$LNUM/ex$(NUM).go; \
	elif [ -f lista$$LNUM/ex$(NUM).cpp ]; then \
		g++ -o lista$$LNUM/ex$(NUM) lista$$LNUM/ex$(NUM).cpp && ./lista$$LNUM/ex$(NUM) && rm -f lista$$LNUM/ex$(NUM); \
	elif [ -f ex$(NUM).go ]; then \
		go run ex$(NUM).go; \
	elif [ -f ex$(NUM).cpp ]; then \
		g++ -o ex$(NUM) ex$(NUM).cpp && ./ex$(NUM) && rm -f ex$(NUM); \
	else \
		echo "No ex$(NUM).go or ex$(NUM).cpp found"; \
	fi

new:
	@if [ -z "$(NUM)" ]; then \
		echo "Usage: make new <exercise name, e.g. 2A>"; \
	else \
		LNUM=$$(echo $(NUM) | grep -o '^[0-9]\+'); \
		mkdir -p lista$$LNUM; \
		if [ -f lista$$LNUM/ex$(NUM).cpp ]; then \
			echo "lista$$LNUM/ex$(NUM).cpp already exists"; \
		else \
			printf '#include <bits/stdc++.h>\nusing namespace std;\n\n#define endl '"'"'\\n'"'"'\n#define ll long long\n\nint main() {\n    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);\n\n}\n' > lista$$LNUM/ex$(NUM).cpp; \
			echo "Created lista$$LNUM/ex$(NUM).cpp"; \
		fi \
	fi

add:
	@LNUM=$$(echo $(EXERCISE) | grep -o '^[0-9]\+'); \
	EX_FILE="ex$(EXERCISE).cpp"; \
	if [ -f lista$$LNUM/ex$(EXERCISE).cpp ]; then \
		EX_FILE="lista$$LNUM/ex$(EXERCISE).cpp"; \
	fi; \
	if [ -z "$(TEMPLATE)" ] || [ -z "$(EXERCISE)" ]; then \
		echo "Usage: make add <template_name> <exercise, e.g. 4A>"; \
	elif [ ! -f templates/$(TEMPLATE).cpp ]; then \
		echo "Template templates/$(TEMPLATE).cpp not found"; \
	elif [ ! -f $$EX_FILE ]; then \
		echo "$$EX_FILE not found"; \
	else \
		LAST_DEFINE=$$(grep -n '^#define' $$EX_FILE | tail -1 | cut -d: -f1); \
		if [ -z "$$LAST_DEFINE" ]; then \
			echo "No #define found in $$EX_FILE"; \
		else \
			sed -i "$${LAST_DEFINE}a\\\n" $$EX_FILE; \
			sed -i "$$(( LAST_DEFINE + 1 ))a\\\n" $$EX_FILE; \
			sed -i "$$(( LAST_DEFINE + 2 ))r templates/$(TEMPLATE).cpp" $$EX_FILE; \
			TMPL_LINES=$$(wc -l < templates/$(TEMPLATE).cpp); \
			AFTER_LINE=$$(( LAST_DEFINE + 2 + TMPL_LINES )); \
			sed -i "$${AFTER_LINE}a\\\n" $$EX_FILE; \
			echo "Added $(TEMPLATE) to $$EX_FILE after line $$LAST_DEFINE"; \
		fi; \
	fi

%:
	@:
