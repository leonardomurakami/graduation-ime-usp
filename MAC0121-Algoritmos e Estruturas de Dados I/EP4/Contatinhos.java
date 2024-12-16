import java.util.*;

public class Contatinhos {
    private static class Contato {
        String nome;
        String instagram;
        String telefone;
        int prioridade;

        public Contato(String nome, String instagram, String telefone, int prioridade) {
            this.nome = nome;
            this.instagram = instagram;
            this.telefone = telefone;
            this.prioridade = prioridade;
        }
        
        public String toString(){
            return this.nome + " - " + this.instagram + " - " + this.telefone + " - prioridade: " + this.prioridade;
        }
    }

    // Indexacao dos contatos ordenados por nome - O(log n) para insercao/busca
    private TreeMap<String, Contato> contatosPorNome;
    
    // Indexacao dos contatos ordenados por Instagram - O(log n) para insercao/busca
    private TreeMap<String, Contato> contatosPorInstagram;
    
    // Indexacao dos contatos ordenados por prioridade - O(log n) para insercao/busca
    private TreeMap<Integer, List<Contato>> contatosPorPrioridade;
    
    // Salvando a ordem de chegada dos usuarios - O(1) para insercao, O(1) para remocao
    private Queue<Contato> contatosPorOrdem;

    public Contatinhos() {
        contatosPorNome = new TreeMap<>();
        contatosPorInstagram = new TreeMap<>();
        contatosPorPrioridade = new TreeMap<>();
        contatosPorOrdem = new LinkedList<>();
    }

    // Adicionar Contato - O(log n)
    public boolean adicionarContato(String nome, String instagram, String telefone, int prioridade) {
        if (prioridade < 1 || prioridade > 100) {
            return false;
        }

        if (contatosPorNome.containsKey(nome) || contatosPorInstagram.containsKey(instagram)) {
            return false;
        }

        Contato novoContato = new Contato(nome, instagram, telefone, prioridade);

        contatosPorNome.put(nome, novoContato); 
        contatosPorInstagram.put(instagram, novoContato);
        contatosPorPrioridade.computeIfAbsent(prioridade, k -> new ArrayList<>()).add(novoContato);
        contatosPorOrdem.offer(novoContato);
        
        return true;
    }

    // Buscar contato - O(log n)
    public Contato buscarContato(String busca) {
        Contato porNome = contatosPorNome.get(busca);
        if (porNome != null) {
            return porNome;
        }
        return contatosPorInstagram.get(busca);
    }

    // Atualizar contato - O(log n)
    public boolean atualizarContato(String nome, String novoInstagram, String novoTelefone, int novaPrioridade) {
        if (novaPrioridade < 1 || novaPrioridade > 100) {
            return false;
        }

        Contato contato = contatosPorNome.get(nome);
        if (contato == null) {
            return false;
        }

        // Se o Instagram esta mudando, verificar se o novo ja existe
        if (!contato.instagram.equals(novoInstagram) && contatosPorInstagram.containsKey(novoInstagram)) {
            return false;
        }

        // Remover das estruturas antigas (nunca acessamos o contato na lista ligada de prioridade)
        // O que mantem O(log n+)
        contatosPorInstagram.remove(contato.instagram);
        contatosPorPrioridade.get(contato.prioridade).remove(contato);
        
        // Atualizar informacoes
        contato.instagram = novoInstagram;
        contato.telefone = novoTelefone;
        contato.prioridade = novaPrioridade;

        // Adicionar nas novas estruturas
        contatosPorInstagram.put(novoInstagram, contato);
        contatosPorPrioridade.computeIfAbsent(novaPrioridade, k -> new ArrayList<>()).add(contato);

        return true;
    }
    
    public void listarContatosPorPrioridade(){
        for (Map.Entry<Integer, List<Contato>> entry : contatosPorPrioridade.entrySet()) {
            for (Contato c : entry.getValue()){
                System.out.println("Contato: " + c.toString());
            }
        }
    }

    // Listar contatos em ordem alfabetica - O(n)
    public void listarContatosOrdemAlfabetica() {
        for (Contato c : contatosPorNome.values()){
            System.out.println("Contato: " + c.toString());
        }
    }

    // Remover primeiro contato - O(log n)
    public boolean removerPrimeiroContato() {
        if (contatosPorOrdem.isEmpty()) {
            return false;
        }
        
        // Pegar o primeiro contato da fila - O(1)
        Contato primeiro = contatosPorOrdem.poll();

        // Remover das estruturas - O(log n)
        contatosPorNome.remove(primeiro.nome);
        contatosPorInstagram.remove(primeiro.instagram);
        contatosPorPrioridade.get(primeiro.prioridade).remove(primeiro);

        return true;
    }
    
    public static void main(String[] args) {
        Contatinho agenda = new Contatinho();
        
        System.out.println("=== Teste 1: Adicionar contatos ===");
        
        System.out.println("Teste 1.1 - Adicionar primeiro contato");
        boolean expected = true;
        boolean real = agenda.adicionarContato("Ana", "@ana", "(11) 1234-4321", 1);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 1.2 - Adicionar contato com mesma prioridade");
        expected = true;
        real = agenda.adicionarContato("Bruno", "@bruno", "(11) 4321-1212", 1);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 1.3 - Adicionar contato com prioridade diferente");
        expected = true;
        real = agenda.adicionarContato("Carlos", "@carlos", "(11) 1199-9821", 2);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        
        agenda.listarContatosOrdemAlfabetica();
        
        System.out.println("\nTeste 1.4 - Tentar adicionar contato com nome duplicado");
        expected = false;
        real = agenda.adicionarContato("Ana", "@ana2", "4444", 1);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 1.5 - Tentar adicionar contato com Instagram duplicado");
        expected = false;
        real = agenda.adicionarContato("Diana", "@ana", "5555", 1);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 1.6 - Tentar adicionar contato com prioridade invalida");
        expected = false;
        real = agenda.adicionarContato("Elena", "@elena", "6666", 101);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\n=== Teste 2: Buscar contatos ===");
        
        System.out.println("Teste 2.1 - Buscar por nome existente");
        String expectedNome = "Ana";
        Contato c1 = agenda.buscarContato("Ana");
        String realNome = c1 != null ? c1.nome : null;
        System.out.println("Expected: " + expectedNome + " | Real: " + realNome + " | " + 
                          (expectedNome.equals(realNome) ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 2.2 - Buscar por Instagram existente");
        expectedNome = "Bruno";
        Contato c2 = agenda.buscarContato("@bruno");
        realNome = c2 != null ? c2.nome : null;
        System.out.println("Expected: " + expectedNome + " | Real: " + realNome + " | " + 
                          (expectedNome.equals(realNome) ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 2.3 - Buscar contato inexistente");
        Contato expectedContato = null;
        Contato realContato = agenda.buscarContato("@inexistente");
        System.out.println("Expected: " + expectedContato + " | Real: " + realContato + " | " + 
                          (expectedContato == realContato ? "PASSED" : "FAILED"));
        
        System.out.println("\n=== Teste 3: Atualizar contatos ===");
        
        System.out.println("Teste 3.1 - Atualizacao normal");
        expected = true;
        real = agenda.atualizarContato("Ana", "@ana_dixx", "(11) 91782-1283", 4);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 3.2 - Verificar dados atualizados");
        String[] expectedDados = {"@ana_dixx", "(11) 91782-1283", "4"};
        Contato c3 = agenda.buscarContato("Ana");
        String[] realDados = {c3.instagram, c3.telefone, String.valueOf(c3.prioridade)};
        boolean dadosCorretos = Arrays.equals(expectedDados, realDados);
        System.out.println("Expected: " + Arrays.toString(expectedDados));
        System.out.println("Real: " + Arrays.toString(realDados));
        System.out.println("Resultado: " + (dadosCorretos ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 3.3 - Tentar atualizar para Instagram existente");
        expected = false;
        real = agenda.atualizarContato("Bruno", "@carlos", "8888", 4);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\n=== Teste 4: Listar por prioridade ===");
        agenda.listarContatosPorPrioridade();
        System.out.println("Ordem esperada de prioridades: 1, 2, 4");
        
        System.out.println("\n=== Teste 5: Listar em ordem alfabetica ===");
        agenda.listarContatosOrdemAlfabetica();
        System.out.println("Ordem esperada de contatos: Ana, Bruno, Carlos");
        
        System.out.println("\n=== Teste 6: Remover primeiro contato ===");
        System.out.println("Teste 6.1 - Remover primeiro contato (Ana)");
        expected = true;
        real = agenda.removerPrimeiroContato();
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 6.2 - Verificar se Ana foi removida");
        expected = true;
        real = (agenda.buscarContato("Ana") == null);
        System.out.println("Expected: " + expected + " | Real: " + real + " | " + (expected == real ? "PASSED" : "FAILED"));
        
        System.out.println("\nTeste 6.3 - Lista final apos remocao");
        agenda.listarContatosOrdemAlfabetica();
        System.out.println("Ordem esperada de contatos: Bruno, Carlos");
    }
}