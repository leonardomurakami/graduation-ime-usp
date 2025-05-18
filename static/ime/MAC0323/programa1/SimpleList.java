public class SimpleList {
    private static class Node {
        String value;
        Node next;
        
        public Node(String value) {
            this.value = value;
            this.next = null;
        }
    }

    private Node head;
    private Node tail;

    public SimpleList() {
        this.head = null;
        this.tail = null;
    }

    public void add(String value) {
        Node newNode = new Node(value);
        
        if (head == null) {
            head = newNode;
            tail = newNode;
            return;
        }
        
        tail.next = newNode;
        tail = newNode;
    }

    public Node getHead() {
        return head;
    }
    
    // checa se o valor existe na lista
    public boolean contains(String value) {
        return find(value) != null;
    }
    
    // encontra e retorna o no contendo o valor, ou null se não encontrado
    public Node find(String value) {
        Node current = head;
        while (current != null) {
            if (current.value.equals(value)) {
                return current;
            }
            current = current.next;
        }
        return null;
    }
    
    // retorna o numero de elementos na lista
    public int size() {
        int count = 0;
        Node current = head;
        while (current != null) {
            count++;
            current = current.next;
        }
        return count;
    }
    
    // retorna todos os valores da lista em um array
    public String[] getValues() {
        String[] values = new String[size()];
        Node current = head;
        int i = 0;
        
        while (current != null) {
            values[i++] = current.value;
            current = current.next;
        }
        
        return values;
    }
    
    // interface para visitar os nos
    // visit(String value) - visita o no com o valor
    public interface NodeVisitor {
        void visit(String value);
    }
    
    public void forEach(NodeVisitor visitor) {
        Node current = head;
        while (current != null) {
            visitor.visit(current.value);
            current = current.next;
        }
    }
}