# EP3 - MAC0323

## Compilação

Para compilar todos os programas:
```bash
make
```

Ou compile individualmente:
```bash
make programa1
make programa2
make programa3
make programa4
```

## Uso dos Programas

### Programa1 - Codificação LaTeX
Converte o texto de entrada usando uma tabela de símbolos LaTeX:
```bash
java Programa1 <arquivo_tabela_simbolos.txt> <arquivo_entrada.txt>
```

**Exemplo:**
```bash
java Programa1 tabela_simbolos.txt teste.txt
```

### Programa2 - Compressão de Huffman
Aplica compressão de Huffman ao texto codificado:
```bash
java Programa2 [--viz] [--output-compressed] <arquivo_entrada>
```

**Opções:**
- `--viz`: Abre visualização gráfica da árvore de Huffman (para debug)
- `--output-compressed`: Salva o texto comprimido no arquivo "compressed"

**Exemplo:**
```bash
java Programa2 --output-compressed out1
```

### Programa3 - Descompressão de Huffman
Descomprime texto usando a árvore de Huffman:
```bash
java Programa3 [--viz] <arquivo_arvore> <arquivo_comprimido>
```

**Opções:**
- `--viz`: Abre visualização gráfica da árvore de Huffman (para debug)

**Exemplo:**
```bash
java Programa3 out2 compressed
```

### Programa4 - Decodificação LaTeX
Converte códigos LaTeX de volta para texto normal:
```bash
java Programa4 <arquivo_codigo_latex> <arquivo_tabela_simbolos>
```

**Exemplo:**
```bash
java Programa4 out3 tabela_simbolos.txt
```

## Pipeline Completo

Para executar todo o processo de codificação → compressão → descompressão → decodificação:

```bash
make test
```

Onde ele utiliza o tabela_simbolos.txt e o texto.txt de inputs e propaga-os para todo o pipeline

Ou execute individualmente:
```bash
make test1  # Programa1: texto.txt → out1
make test2  # Programa2: out1 → out2 + compressed
make test3  # Programa3: out2 + compressed → out3
make test4  # Programa4: out3 → out4
```

## Limpeza

Para remover arquivos compilados e temporários:
```bash
make clean
```
