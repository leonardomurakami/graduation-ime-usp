saida = ""

class Node:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

def construct_code(vec, node, code):
    if node.left is None and node.right is None:
        vec[node.char] = code
        return
    construct_code(vec, node.left, code + '0')
    construct_code(vec, node.right, code + '1')

def write_tree(node):
    global saida
    if node.left is None and node.right is None:
        saida += '1'
        saida += format(ord(node.char), '08b')
        return
    saida += '0'
    write_tree(node.left)
    write_tree(node.right)

def write_code(string, code):
    out = ""
    for char in string:
        out += code[char]
    return out

def main():
    string = """vc
merece
3
mendigos
pelados
na
rua
atras de vc
toda manha de terca feira"""
    freq = {}
    nodes = []
    for char in string:
        if char not in freq:
            freq[char] = 0
        freq[char] += 1

    nodes = []
    for char, freq in freq.items():
        nodes.append(Node(char, freq))
    
    while len(nodes) > 1:
        nodes.sort(key=lambda x: x.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)
        nodes.append(Node(char="", freq=left.freq + right.freq, left=left, right=right))

    codes = {}
    huffman_tree = nodes[0]
    construct_code(codes, huffman_tree, "")
    write_tree(huffman_tree)
    print("Arvore:")
    print(saida)
    out = write_code(string, codes)
    print("Comprimido:")
    print(out)

main()