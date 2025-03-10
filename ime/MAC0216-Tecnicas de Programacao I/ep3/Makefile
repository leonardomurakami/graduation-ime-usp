# Configuracao do python
PYTHON = python3
PYTEST = pytest

# Configuracao da documentacao
DOXYGEN = doxygen
DOC_DIR = docs
DOC_CONFIG = Doxyfile

# Diretorios de codigo
SRC_DIR = src
TEST_DIR = tests

# Arquivos a serem limpos
CLEAN_FILES = $(DOC_DIR) .coverage .pytest_cache **/__pycache__ htmlcov Doxyfile **.pkl **.db

.PHONY: all doc tests clean

# Comando padrao
all: doc tests

# Gera documentacao com doxygen
doc: $(DOC_CONFIG)
	@echo "Generating documentation..."
	@mkdir -p $(DOC_DIR)
	@$(DOXYGEN) $(DOC_CONFIG)
	@echo "Documentation generated in $(DOC_DIR)/"

# Cria a doxyfile se ela nao existir
$(DOC_CONFIG):
	@echo "Creating Doxygen configuration file..."
	@$(DOXYGEN) -g $(DOC_CONFIG)
	@sed -i 's/PROJECT_NAME.*=.*/PROJECT_NAME = "Textris"/' $(DOC_CONFIG)
	@sed -i 's/OUTPUT_DIRECTORY.*=.*/OUTPUT_DIRECTORY = docs/' $(DOC_CONFIG)
	@sed -i 's/EXTRACT_ALL.*=.*/EXTRACT_ALL = YES/' $(DOC_CONFIG)
	@sed -i 's/RECURSIVE.*=.*/RECURSIVE = YES/' $(DOC_CONFIG)
	@sed -i 's/GENERATE_HTML.*=.*/GENERATE_HTML = YES/' $(DOC_CONFIG)
	@sed -i 's/GENERATE_LATEX.*=.*/GENERATE_LATEX = NO/' $(DOC_CONFIG)
	@sed -i 's/OUTPUT_LANGUAGE.*=.*/OUTPUT_LANGUAGE = Brazilian/' $(DOC_CONFIG)
	@sed -i 's/INPUT.*=.*/INPUT = README.md src main.py/' $(DOC_CONFIG)
	@sed -i 's/USE_MDFILE_AS_MAINPAGE.*=.*/USE_MDFILE_AS_MAINPAGE = "README.md"/' $(DOC_CONFIG)
	@sed -i 's/MARKDOWN_SUPPORT.*=.*/MARKDOWN_SUPPORT = YES/' $(DOC_CONFIG)

# Roda os testes
tests:
	@echo "Running tests..."
	@$(PYTEST) -v

# Roda o jogo
run: 
	@echo "Running game..."
	@$(PYTHON) main.py

# Instala as dependencias
deps:
	@echo "Installing requirements..."
	@pip install -r requirements.txt

# Limpa arquivos
clean:
	@echo "Cleaning generated files..."
	@rm -rf $(CLEAN_FILES)
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"