#ifndef USPSH_H
#define USPSH_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <pwd.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <fcntl.h>
#include <errno.h>
#include <limits.h>

#define MAX_COMMAND_LENGTH 1024
#define MAX_ARGS 64

// Função para obter o prompt do shell
char* get_prompt();

// Função para analisar a linha de comando em tokens
int parse_input(char *input, char **args);

// Função para executar comandos externos
int execute_external_command(char **args);

// Funções para comandos internos
int execute_cd(char *directory);
int execute_whoami();
int execute_chmod(char *permissions, char *path);

// Função principal para executar comandos
int execute_command(char **args);

#endif // USPSH_H