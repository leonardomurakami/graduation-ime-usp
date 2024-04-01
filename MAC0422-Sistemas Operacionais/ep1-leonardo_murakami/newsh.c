#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pwd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/utsname.h>
#include <time.h>
#include <readline/readline.h>
#include <readline/history.h>
#include "scheduler.h"

#define MAX_ARG_SIZE 10
#define MAX_CMD_SIZE 256
#define TRUE 1
#define FALSE 0

void execute_external_command(char *cmd) {
    pid_t pid = fork();
    if (pid == 0) {
        if (execl(cmd, cmd, (char *)NULL) == -1) {
            perror(cmd);
            exit(EXIT_FAILURE);
        }
    } else if (pid > 0) {
        int status;
        waitpid(pid, &status, 0);
    } else {
        perror(cmd);
    }
}

int execute_builtin_command(char **args) {
    if (strcmp(args[0], "cd") == 0) {
        if (chdir(args[1]) != 0) {
            perror("newsh");
        }
        return 1;
    }
    if (strcmp(args[0], "rm") == 0) {
        if (unlink(args[1]) != 0) {
            perror("newsh");
        }
        return 1;
    }
    if (strcmp(args[0], "uname") == 0 && strcmp(args[1], "-a") == 0) {
        struct utsname buffer;
        if (uname(&buffer) != 0) {
            perror("newsh");
        } else {
            printf("%s %s %s %s %s\n", buffer.sysname, buffer.nodename, buffer.release, buffer.version, buffer.machine);
        }
        return 1;
    }
    if (strcmp(args[0], "run") == 0) {
        if (args[1] == NULL || args[2] == NULL || args[3] == NULL) {
            printf("Uso: run <tipo_escalonador> <arquivo_entrada> <arquivo_saida>\n");
        } else {
            int schedulerAlgorithm = atoi(args[1]);
            executeScheduler(schedulerAlgorithm, args[2], args[3]);
        }
        return 1;
    }

    return 0;
}

void process_input(char *input) {
    char *args[MAX_ARG_SIZE];
    char *token = strtok(input, " ");
    int i = 0;

    while (token != NULL && i < MAX_ARG_SIZE) {
        args[i++] = token;
        token = strtok(NULL, " ");
    }
    args[i] = NULL;

    if (args[0] == NULL) {
        return;
    }

    if (!execute_builtin_command(args)) {
        execute_external_command(input);
    }
}


char *generate_prompt() {
    static char prompt[MAX_CMD_SIZE];
    time_t now = time(NULL);
    struct tm *tm_struct = localtime(&now);

    char time_buffer[9];
    strftime(time_buffer, sizeof(time_buffer), "%H:%M:%S", tm_struct);

    snprintf(prompt, sizeof(prompt), "%s [%s]: ", getenv("USER"), time_buffer);
    return prompt;
}

int main() {
    char *input;
    using_history();

    while (1) {
        input = readline(generate_prompt());

        if (!input) break;

        if (*input) {
            add_history(input);
            process_input(input);
        }

        free(input);
    }

    return 0;
}
