public class MyHashTable {
    private static class Node {
        String key;
        Object value;
        Node next;
        
        public Node(String key, Object value) {
            this.key = key;
            this.value = value;
            this.next = null;
        }
    }

    private Node[] table;
    private int capacity;

    public MyHashTable(int capacity) {
        this.capacity = capacity;
        this.table = new Node[capacity];
    }

    private int hash(String key) {
        if (key == null) return 0;
        
        int hash = 0;
        for (int i = 0; i < key.length(); i++) {
            hash = (31 * hash + key.charAt(i)) % capacity;
        }
        return Math.abs(hash % capacity);
    }

    private Node findNode(String key) {
        int index = hash(key);
        
        Node current = table[index];
        while (current != null) {
            if (current.key.equals(key)) {
                return current;
            }
            current = current.next;
        }
        
        return null;
    }

    private Node findLastNode(int index) {
        if (table[index] == null) {
            return null;
        }
        
        Node current = table[index];
        while (current.next != null) {
            current = current.next;
        }
        
        return current;
    }

    public void put(String key, Object value) {
        int index = hash(key);
        
        if (table[index] == null) {
            table[index] = new Node(key, value);
            return;
        }
        
        Node existingNode = findNode(key);
        if (existingNode != null) {
            existingNode.value = value;
            return;
        }
        
        Node lastNode = findLastNode(index);
        lastNode.next = new Node(key, value);
    }

    public Object get(String key) {
        Node node = findNode(key);
        return node != null ? node.value : null;
    }

    public boolean contains(String key) {
        return findNode(key) != null;
    }
}