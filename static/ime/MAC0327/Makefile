NUM = $(filter-out $@,$(MAKECMDGOALS))

run:
	@if [ -f ex$(NUM).go ]; then \
		go run ex$(NUM).go; \
	elif [ -f ex$(NUM).cpp ]; then \
		g++ -o ex$(NUM) ex$(NUM).cpp && ./ex$(NUM) && rm -f ex$(NUM); \
	else \
		echo "No ex$(NUM).go or ex$(NUM).cpp found"; \
	fi

new:
	@if [ -z "$(NUM)" ]; then \
		echo "Usage: make new <exercise name, e.g. 2A>"; \
	elif [ -f ex$(NUM).cpp ]; then \
		echo "ex$(NUM).cpp already exists"; \
	else \
		printf '#include <bits/stdc++.h>\nusing namespace std;\n\n#define endl '"'"'\\n'"'"'\n#define ll long long\n\nint main() {\n    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);\n\n}\n' > ex$(NUM).cpp; \
		echo "Created ex$(NUM).cpp"; \
	fi

%:
	@:
