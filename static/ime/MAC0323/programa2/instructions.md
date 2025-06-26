Programa 2: Geração de Árvore de Compressão de Huffman
O objetivo deste programa é criar uma "chave" de compressão, na forma de uma árvore de Huffman, a partir de uma mensagem codificada com símbolos LaTeX. Esta tarefa reflete os desafios enfrentados pelos "guerrilheiros digitais", que precisavam decifrar mensagens comprimidas para executar seus planos.


Descrição Detalhada
O programa recebe um arquivo de texto (.txt) como entrada. Este arquivo contém uma única string formada por códigos LaTeX (como 

$\bowtie$) e pontos, que é exatamente o formato de saída do Programa 1. A partir desta entrada, o programa deve executar duas etapas principais:




Análise de Frequência: O programa deve primeiro analisar a string de entrada para contar a frequência de cada "símbolo". No contexto deste problema, um "símbolo" não é uma letra individual, mas sim cada código LaTeX completo (ex: 


$\blacklozenge$) e o caractere de ponto (.). No enredo, os personagens percebem que a codificação era baseada em "palavras" (os códigos LaTeX) e não em caracteres individuais.




Construção da Árvore de Huffman: Utilizando as frequências calculadas, o programa deve construir uma árvore de compressão de Huffman. O algoritmo de Huffman cria uma árvore binária de prefixo ótima, onde os símbolos mais frequentes são posicionados mais perto da raiz, resultando em códigos binários mais curtos para eles. Cada folha da árvore representará um dos códigos LaTeX ou o ponto.



Formato da Saída
A saída do programa deve ser uma única string que representa a árvore de Huffman serializada. A serialização é feita através de uma travessia em pré-ordem da árvore, seguindo estas regras:

Ao encontrar um nó interno, adicione um 0 à string de saída.

Ao encontrar um 

nó folha, adicione um 1 à string de saída, seguido imediatamente pelo símbolo (o código LaTeX ou o ponto) que aquela folha representa.



Exemplo Prático
O documento fornece um exemplo claro para ilustrar o processo:


Entrada (Saída do Programa 1):



$\bowtie$$\blacklozenge$$\wp$$\blacklozenge$.$\spadesuit$$\pitchfork$$\bowtie$$\blacklozenge$.$\bowtie$$\blacklozenge$$\wp$$\blacklozenge$.$\spadesuit$$\pitchfork$$\bowtie$$\blacklozenge$

Processo:

O programa calcularia a frequência de cada código. Por exemplo, 

$\bowtie$ é o mais frequente, aparecendo 6 vezes, enquanto $\spadesuit$ e $\pitchfork$ são menos frequentes.

Com base nessas frequências, a árvore de Huffman é construída.


Saída (Árvore Serializada):


001$\blacklozenge$1$\bowtie$001$\spadesuit$1.01$\wp$1$\pitchfork$

Esta string de saída é a representação da árvore que será usada pelo Programa 3 para decodificar uma mensagem binária de volta para os símbolos LaTeX.