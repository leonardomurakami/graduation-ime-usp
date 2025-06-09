import java.util.Iterator;
import java.util.NoSuchElementException;

public class SimpleList implements Iterable<String> {
    private static class Node {
        String value;
        Node next;
    }

    private Node head;

    public void add(String value) {
        Node newNode = new Node();
        newNode.value = value;
        newNode.next = head;
        head = newNode;
    }
    
    @Override
    public Iterator<String> iterator() { return new IteratorType();}

    public class IteratorType implements Iterator<String> {
        private Node current = head; // Current node starts at the head

        @Override
        public boolean hasNext() {
            return current != null;
        }

        @Override
        public String next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            String value = current.value;
            current = current.next;
            return value;
        }
    }
}