#include "uspsh.h"

int main() {
    char *input;
    char *args[MAX_ARGS];
    int status = 1;

    // Inicializar a biblioteca readline para histórico de comandos
    using_history();

    while (status) {
        // Obter o prompt personalizado
        char *prompt = get_prompt();
        
        // Ler a entrada do usuário usando readline
        input = readline(prompt);
        
        // Adicionar ao histórico apenas se não for uma linha vazia
        if (input && *input) {
            add_history(input);
        }
        
        // Liberar a memória do prompt
        free(prompt);
        
        // Se não houver entrada, continuar
        if (!input) {
            status = 0;
            printf("\n");
            continue;
        }
        
        // Se a entrada estiver vazia, continuar
        if (input[0] == '\0') {
            free(input);
            continue;
        }
        
        // Analisar a entrada
        int arg_count = parse_input(input, args);
        
        // Verificar se há argumentos
        if (arg_count > 0) {
            // Executar o comando
            status = execute_command(args);
        }
        
        // Liberar a memória da entrada
        free(input);
    }
    
    // Limpar o histórico antes de sair
    clear_history();
    
    return EXIT_SUCCESS;
}

// Função para obter o nome do computador usando chamada de sistema uname
char* get_hostname() {
    static char hostname[HOST_NAME_MAX];
    
    // Usar a chamada de sistema gethostname() para obter o nome do computador
    // Se falhar, retorna "unknown"
    if (gethostname(hostname, HOST_NAME_MAX) != 0) {
        strcpy(hostname, "unknown");
    }
    
    return hostname;
}

// Função para obter o diretório atual usando chamada de sistema getcwd
char* get_current_directory() {
    static char cwd[PATH_MAX];
    
    // Usar a chamada de sistema getcwd() para obter o diretório atual
    if (getcwd(cwd, PATH_MAX) == NULL) {
        strcpy(cwd, "unknown");
    }
    
    return cwd;
}

// Função para construir o prompt do shell
char* get_prompt() {
    // Obter o nome do computador e o diretório atual
    char *hostname = get_hostname();
    char *cwd = get_current_directory();
    
    // Construir o prompt no formato [hostname:diretório]$
    char *prompt = malloc(strlen(hostname) + strlen(cwd) + 10);
    if (prompt == NULL) {
        perror("Falha na alocação de memória");
        exit(EXIT_FAILURE);
    }
    
    sprintf(prompt, "[%s:%s]$ ", hostname, cwd);
    
    return prompt;
}

// Função para analisar a entrada em tokens
int parse_input(char *input, char **args) {
    int arg_count = 0;
    char *token;
    
    // Dividir a entrada em tokens por espaços em branco
    token = strtok(input, " \t\n");
    while (token != NULL && arg_count < MAX_ARGS - 1) {
        args[arg_count] = token;
        arg_count++;
        token = strtok(NULL, " \t\n");
    }
    
    // Marcar o final da lista de argumentos
    args[arg_count] = NULL;
    
    return arg_count;
}

// Implementação do comando interno cd usando chdir()
int execute_cd(char *directory) {
    // Usar a chamada de sistema chdir() para mudar o diretório atual
    if (chdir(directory) != 0) {
        perror("cd");
        return 1;
    }
    return 1;
}

// Implementação do comando interno whoami usando getuid()
int execute_whoami() {
    // Usar a chamada de sistema getuid() para obter o ID do usuário
    uid_t uid = getuid();
    
    // Obter informações do usuário a partir do ID
    struct passwd *pw = getpwuid(uid);
    
    if (pw == NULL) {
        perror("whoami");
        return 1;
    }
    
    // Imprimir o nome do usuário
    printf("%s\n", pw->pw_name);
    
    return 1;
}

// Implementação do comando interno chmod usando chmod()
int execute_chmod(char *permissions, char *path) {
    // Converter a permissão em octal para decimal
    mode_t mode = strtol(permissions, NULL, 8);
    
    // Usar a chamada de sistema chmod() para alterar as permissões do arquivo ou diretório
    if (chmod(path, mode) != 0) {
        perror("chmod");
        return 1;
    }
    
    return 1;
}

// Função para executar comandos externos
int execute_external_command(char **args) {
    pid_t pid;
    int status;
    
    // Criar um processo filho
    pid = fork();
    
    if (pid == 0) {
        // Código do processo filho
        if (execvp(args[0], args) == -1) {
            perror("execvp");
            exit(EXIT_FAILURE);
        }
    } else if (pid < 0) {
        // Erro ao criar o processo filho
        perror("fork");
    } else {
        // Código do processo pai
        // Esperar pelo término do processo filho
        do {
            waitpid(pid, &status, WUNTRACED);
        } while (!WIFEXITED(status) && !WIFSIGNALED(status));
    }
    
    return 1;
}

int execute_command(char **args) {
    // Verificar comandos que rodam com syscalls
    
    // Comando interno cd
    if (strcmp(args[0], "cd") == 0) {
        if (args[1] == NULL) {
            fprintf(stderr, "cd: falta o argumento do diretório\n");
        } else {
            return execute_cd(args[1]);
        }
        return 1;
    }
    
    // Comando interno whoami
    if (strcmp(args[0], "whoami") == 0) {
        return execute_whoami();
    }
    
    // Comando interno chmod
    if (strcmp(args[0], "chmod") == 0) {
        if (args[1] == NULL || args[2] == NULL) {
            fprintf(stderr, "chmod: falta argumentos\n");
        } else {
            return execute_chmod(args[1], args[2]);
        }
        return 1;
    }
    
    // Para qualquer outro comando, executar como comando externo
    return execute_external_command(args);
}