# Textris - Um Tetris em Modo Texto

## Visão Geral
Textris é uma implementação em Python do clássico jogo Tetris que oferece tanto uma interface em modo texto quanto uma interface gráfica (usando PyGame). O projeto tem como objetivo fornecer uma implementação limpa, modular e bem documentada do Tetris.

## Funcionalidades
- Dois modos de visualização:
  - Interface em modo texto para jogar no terminal
  - Interface gráfica utilizando PyGame
- Implementação completa de todas as peças padrão do Tetris (I, J, L, O, S, T, Z)
- Sistema de pontuação com ranking dos melhores jogadores (localmente)
- Possibilidade de salvar e carregar jogos
- Visualização das próximas peças

## Como Jogar

### Requisitos do Sistema
- Python 3.10.14 ou superior
- Make (para usar os comandos do Makefile)
- Doxygen (para gerar a documentação)

### Ambiente de Desenvolvimento
- Esse programa foi desenvolvido primariamente numa maquina rodando WSL e em um ubuntu 22.04

### Instalação e Execução

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd MAC0216-Tecnicas de Programacao I/programa3
```

2. Instale as dependências usando o comando make:
```bash
make deps
```
Este comando instalará todas as bibliotecas necessárias (pytest, pygame, readchar) automaticamente.

3. Para executar o jogo:
```bash
make run
```

### Comandos Make Disponíveis
- `make all`: Gera a documentação e executa os testes
- `make doc`: Gera apenas a documentação usando Doxygen
- `make tests`: Executa os testes unitários
- `make run`: Inicia o jogo
- `make deps`: Instala as dependências necessárias
- `make clean`: Remove arquivos gerados (documentação, cache, arquivos temporários)

### Controles
- Left/Right: Mover peça para esquerda/direita
- Down: Mover peça para baixo
- Up: Rotacionar peça
- S: Sair do jogo
- G: Salvar jogo

## Desenvolvimento
### Estrutura do Projeto
```
textris/
├── main.py           # Ponto de entrada do jogo
├── src/
│   ├── board.py      # Implementação do tabuleiro
│   ├── controller.py # Controlador do jogo
│   ├── game.py       # Lógica principal do jogo
│   ├── pieces.py     # Definição das peças
│   ├── scores.py     # Sistema de pontuação
│   └── views.py      # Interfaces gráfica e texto
├── tests/            # Testes unitários
└── docs/            # Documentação
```

### Documentação
A documentação completa do código pode ser gerada usando Doxygen:
```bash
make doc
```
A documentação será gerada na pasta `docs/` e pode ser acessada abrindo o arquivo `docs/html/index.html` em um navegador.

### Testes
Para executar os testes unitários:
```bash
make tests
```

### Limpeza
Para limpar todos os arquivos gerados (documentação, cache, etc.):
```bash
make clean
```

## Autor
Leonardo Heidi Almeida Murakami 
  - NUSP: 11260186
  - e-mail: 
    - leonardo.murakami@usp.br
    - contato@murakams.com

## Agradecimentos
- Desenvolvido como projeto para a disciplina MAC0216 - Tecnicas de Programacao I do Instituto de Matematica e Estatistica durante o curso de Bacharelado em ciencia da computacao ministrada pela professora Kelly Rosa Braghetto
- Inspirado no clássico jogo Tetris criado por Alexey Pajitnov