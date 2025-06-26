# MAC0422 - Sistemas Operacionais 1s2025

## EP4 (Individual)

**Data de entrega:** 1/7/2025 até 13:00:00
**Prof. Daniel Macêdo Batista**

-----

### 1 Problema

A tarefa neste EP é avaliar o desempenho de servidores de echo concorrentes implementados usando as diferentes abordagens para comunicação entre processos que foram vistas em sala de aula: Internet Sockets com múltiplos processos, Internet Sockets com múltiplas threads, Internet Sockets com multiplexação de Entrada e Saída e Unix Domain Sockets.

Você não precisará implementar esses servidores e nem os respectivos clientes. Todos esses códigos já estão disponíveis na área do EP no e-Disciplinas. A sua tarefa será implementar um bash script que vai executar os vários servidores, gerar gráficos utilizando o gnuplot para comparar os tempos necessários para cada servidor fornecer o serviço para clientes concorrentes e fazer um vídeo mostrando o seu script em funcionamento e analisando os resultados obtidos, explicando se os resultados coincidem com o esperado. O bash script deve ser implementado de modo a ser executado no GNU/Linux.

-----

### 2 Requisitos

O seu bash script deverá receber n argumentos em linha de comando. Um primeiro argumento obrigatório que diz respeito à quantidade de clientes concorrentes que deverão ser executados. Em seguida, $n-1$ argumentos que dizem respeito aos tamanhos dos arquivos que serão passados como entrada para o cliente que, por sua vez, enviará para o servidor ecoar de volta.

Abaixo está um exemplo de execução do bash script informando que serão executados 10 clientes concorrentes enviando arquivos de 5MB e de 10MB para os servidores. Todas as mensagens que seguem deverão ser impressas pelo seu bash script exatamente da mesma forma como apresentado. As mensagens deixam claro quais são as etapas que precisam ser realizadas pelo bash script e serão detalhadas a seguir:

```bash
$./ep4.sh 10 5 10 
Compilando ep4-servidor-inet_processos 
Compilando ep4-servidor-inet_threads 
Compilando ep4-servidor-inet_muxes 
Compilando ep4-servidor-unix_threads 
Compilando ep4-cliente-inet 
Compilando ep4-cliente-unix 
>>>>>>> Gerando um arquivo texto de: 5MB... 
Subindo o servidor ep4-servidor-inet_processos 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 5MB... 
Esperando os clientes terminarem. 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-inet_processos: 00:01 
Enviando um sinal 15 para o servidor ep4-servidor-inet_processos...
Subindo o servidor ep4-servidor-inet_threads 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 5MB... 
Esperando os clientes terminarem... 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-inet_threads: 00:01 
Enviando um sinal 15 para o servidor ep4-servidor-inet_threads... 
Subindo o servidor ep4-servidor-inet_muxes 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 5MB... 
Esperando os clientes terminarem. 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-inet_muxes: 00:02 
Enviando um sinal 15 para o servidor ep4-servidor-inet_muxes... 
Subindo o servidor ep4-servidor-unix_threads 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 5MB... 
Esperando os clientes terminarem... 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-unix_threads: 00:01 
Enviando um sinal 15 para o servidor ep4-servidor-unix_threads... 
>>>>>>> Gerando um arquivo texto de: 10MB... 
Subindo o servidor ep4-servidor-inet_processos 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 10MB... 
Esperando os clientes terminarem. 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-inet_processos: 00:03 
Enviando um sinal 15 para o servidor ep4-servidor-inet_processos... 
Subindo o servidor ep4-servidor-inet_threads 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 10MB... 
Esperando os clientes terminarem... 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-inet_threads: 00:03 
Enviando um sinal 15 para o servidor ep4-servidor-inet_threads... 
Subindo o servidor ep4-servidor-inet_muxes 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 10MB... 
Esperando os clientes terminarem. 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-inet_muxes: 00:03 
Enviando um sinal 15 para o servidor ep4-servidor-inet_muxes... 
Subindo o servidor ep4-servidor-unix_threads 
>>>>>>> Fazendo 10 clientes ecoarem um arquivo de: 10MB... 
Esperando os clientes terminarem.. 
Verificando os instantes de tempo no journald... 
>>>>>>> 10 clientes encerraram a conexão 
>>>>>>> Tempo para servir os 10 clientes com o ep4-servidor-unix_threads: 00:01 
Enviando um sinal 15 para o servidor ep4-servidor-unix_threads... 
>>>>>>> Gerando o gráfico de 10 clientes com arquivos de: 5MB 10MB 
```

#### 2.1 Compilação dos códigos 

O arquivo `ep4-clientes+servidores.tar.gz` contém os seguintes arquivos: 

  * `ep4-clientes+servidores/ep4-servidor-inet_processos.c`: Servidor de echo concorrente com sockets da Internet e `fork` para cada cliente. 
  * `ep4-clientes+servidores/ep4-servidor-inet_threads.c`: Servidor de echo concorrente com sockets da Internet e `pthread_create` para cada cliente. 
  * `ep4-clientes+servidores/ep4-servidor-inet_muxes.c`: Servidor de echo concorrente com sockets da Internet e multiplexação via `select`. 
  * `ep4-clientes+servidores/ep4-servidor-unix_threads.c`: Servidor de echo concorrente com sockets de Domínio Unix e `pthread_create` para cada cliente. 
  * `ep4-clientes+servidores/ep4-cliente-unix.c`: Cliente de echo para servidores com sockets da Internet. 
  * `ep4-clientes+servidores/ep4-cliente-inet.c`: Cliente de echo para servidor com sockets de Domínio Unix. 

Você deve ler os códigos para entendê-los.  Não é necessário modificá-los.  Compile e teste cada par cliente-servidor manualmente para garantir o funcionamento.  Monitore as mensagens do servidor com `journalctl`.  Após confirmar que o eco funciona, encerre o cliente com `CTRL+d` e o servidor com o sinal 15.  O cliente para `ep4-servidor-unix_threads.c` é o `ep4-cliente-unix.c`. 

Depois dos testes manuais, automatize a compilação no seu script.  O script deve assumir que os arquivos-fonte estão no diretório `ep4-clientes+servidores/`.  Os binários devem ser criados no diretório `/tmp` e ter o mesmo nome dos arquivos-fonte, mas sem a extensão `.c`. 

#### 2.2 Geração dos arquivos que serão ecoados 

O script deve gerar arquivos de texto puro no diretório `/tmp` com os tamanhos em MB especificados na linha de comando.  Pode-se usar qualquer comando padrão do GNU/Linux para isso.  Uma sugestão para criar um arquivo de 1KB é: 

```bash
$ base64 /dev/urandom | head -c 1024 > /tmp/arquivo_de_1KB.txt 
$ echo >> /tmp/arquivo_de_1KB.txt 
```

Nomeie os arquivos de forma a incluir seu tamanho para facilitar a depuração (ex: `05MB.txt`).  O laço mais externo do script deve iterar sobre os tamanhos dos arquivos. 

#### 2.3 Execução dos servidores 

Cada servidor deve ser testado individualmente, garantindo que não haja outras instâncias rodando.  O laço para os servidores deve ser o segundo laço do script, dentro do laço de tamanhos de arquivo. 

#### 2.4 Execução dos clientes concorrentes 

Com um servidor no ar, o script deve executar a quantidade de clientes informada, em segundo plano.  Isso requer um terceiro laço, de 1 até o número de clientes, dentro do laço dos servidores.  A saída padrão e a saída de erro dos clientes devem ser suprimidas para não poluir o terminal.  Exemplo de execução de um cliente em segundo plano com redirecionamento de entrada e supressão de saída: 

```bash
$ /tmp/ep4-cliente-inet 127.0.0.1 < /tmp/nome_do_arquivo &>/dev/null & 
```

#### 2.5 Aguardando os clientes terminarem 

Após iniciar todos os clientes, um outro laço é necessário para esperar que eles terminem.  Se usar o comando `ps` para monitorar, inclua um `sleep` na iteração para evitar espera ocupada. 

#### 2.6 Contabilização do tempo que o servidor levou para atender todos os clientes

Após a finalização dos clientes, use o `journalctl` para verificar os logs do servidor.  É preciso encontrar o instante de tempo em que o primeiro cliente começou a ser atendido e o instante em que o último cliente finalizou, para calcular o tempo total de atendimento.  É importante ler o código dos servidores para saber quais mensagens de log marcam o início e o fim de um serviço. 

**Dicas:**

  * Use `journalctl` com o parâmetro `-q` para remover mensagens irrelevantes e `--since` com a hora de início do servidor para filtrar logs. 
  * Para registrar a hora de início do servidor, use o comando `/bin/date` logo após executá-lo. 
  * Para calcular a diferença de tempo no formato `mm:ss` (necessário para o eixo y do gráfico), utilize o programa `dateutils.diff`.  Este programa estará disponível no ambiente de correção. 
    ```bash
    $ dateutils.ddiff "2025-02-18 23:43:21" "2025-02-19 00:15:35" -f "%OM:%S" 
    32:14
    ```

Após coletar o tempo, armazene o valor e encerre o servidor enviando o sinal 15. 

#### 2.7 Geração do gráfico 

O script deve gerar um gráfico em formato PDF usando o `gnuplot`.  Abaixo um exemplo de gráfico para 100 clientes com arquivos de 5MB a 35MB. 

 

Para gerar o gráfico, o `gnuplot` precisa de um arquivo de configuração (com extensão `.gpi`).  O script deverá criar este arquivo no `/tmp`.  Exemplo de arquivo `.gpi`: 

```gnuplot
set ydata time 
set timefmt "%M:%S" 
set format y "%M:%S" 
set xlabel 'Dados transferidos por cliente (MB)' 
set ylabel 'Tempo para atender 100 clientes concorrentes' 
set term pdfcairo 
set output "ep4-resultados-100.pdf" 
set grid 
set key top left 
plot "/tmp/ep4-resultados-100.data" using 1:4 with linespoints title "Sockets da Internet: Mux de E/S",\
 "/tmp/ep4-resultados-100.data" using 1:3 with linespoints title "Sockets da Internet: Threads",\
 "/tmp/ep4-resultados-100.data" using 1:2 with linespoints title "Sockets da Internet: Processos",\
 "/tmp/ep4-resultados-100.data" using 1:5 with linespoints title "Sockets Unix: Threads" 
```

O arquivo `.gpi` acima utiliza um arquivo de dados (com extensão `.data`), que também deve ser gerado pelo script no `/tmp`.  O formato deve ser compatível com o `gnuplot`.  Exemplo de arquivo `.data`: 

```
05 00:31 00:29 00:44 00:20 
10 01:02 01:00 01:31 00:40 
15 01:29 01:25 02:09 00:57 
20 02:04 02:04 03:00 01:20 
25 02:31 02:37 03:40 01:38
30 03:14 03:13 04:28 02:03
35 03:46 03:50 05:12 02:30
```

É possível utilizar outros formatos para o arquivo de dados, desde que o arquivo `.gpi` seja ajustado.  A documentação do `gnuplot` pode ser acessada com o comando `gnuplot` seguido de `help`. 

#### 2.8 Término do script 

Ao final, o script deve remover todos os arquivos temporários gerados.  Os únicos arquivos novos que devem permanecer no diretório são os gráficos em PDF.  O script deve sair com o código 0 em caso de sucesso. 

-----

### 3 Sobre a entrega 

A entrega deve ser um único arquivo `.tar.gz`.  Entregas que não sigam o formato e os nomes de arquivos especificados receberão nota ZERO.  O conteúdo do arquivo `.tar.gz` deve ser:

  * **1 arquivo `ep4.sh`:** A implementação do script. 
  * **5 arquivos PDF:** `ep4-resultados-100.pdf`, `ep4-resultados-200.pdf`, `ep4-resultados-300.pdf`, `ep4-resultados-400.pdf`, e `ep4-resultados-500.pdf`.  Estes são os resultados da execução do script para 100, 200, 300, 400 e 500 clientes concorrentes, todos transferindo arquivos de 5, 10, 15, 20, 25, 30 e 35MB.  O script precisará ser executado 5 vezes para gerar estes arquivos. 
  * **1 arquivo `LEIAME`:** Em formato texto, explicando como rodar o script e contendo um link para um vídeo de no máximo 10 minutos. 

**Requisitos do Vídeo (vale 3,0 pontos):** 

  * Deve ser hospedado no YouTube ou Google Drive (não inclua o arquivo de vídeo no `.tar.gz`). 
  * O link deve ser compartilhado no arquivo `LEIAME`. 
  * Inicie o vídeo executando o comando `md5sum` em todos os arquivos entregues (o script e os 5 PDFs) para provar que são os mesmos da submissão.  A não coincidência dos hashes resultará em nota ZERO. 
  * Demonstre a execução do script com os parâmetros `10 5 10`. 
  * Analise os resultados do gráfico da demonstração e dos 5 gráficos entregues, justificando com a teoria vista em aula.  Explique a progressão dos resultados com o aumento do tamanho dos arquivos e do número de clientes. 
  * Não utilize slides; explique diretamente sobre os gráficos. 
  * Use um software de captura de tela como o OBS. 
  * Garanta que o vídeo tenha permissão de acesso para o professor (batista@ime.usp.br) e os monitores. 

**Ambiente de Teste:**

  * Para garantir medições consistentes, evite rodar outros programas que consumam muitos recursos durante a execução dos experimentos e a gravação do vídeo. 

**Formato do Arquivo de Entrega:**

  * O descompactamento do `.tar.gz` deve criar um diretório chamado `ep4-seu nome` (ex: `ep4-artur avila`). 
  * Entregas que sejam "tarbombs" ou que criem um diretório com nome incorreto terão a nota penalizada. 
  * Não inclua arquivos não solicitados (como diretórios `.git`, arquivos `.gitignore`, binários, códigos-fonte dos clientes/servidores, etc.). A presença de arquivos extras resultará em desconto na nota. 

A entrega deve ser feita pelo e-Disciplinas.  O trabalho é individual. 