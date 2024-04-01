#ifndef NEWSH_H
#define NEWSH_H

#define MAX_ARG_SIZE 10
#define MAX_CMD_SIZE 256

void execute_external_command(char *cmd);
int execute_builtin_command(char **args);
void process_input(char *input);
char *generate_prompt();

#endif // NEWSH_H
