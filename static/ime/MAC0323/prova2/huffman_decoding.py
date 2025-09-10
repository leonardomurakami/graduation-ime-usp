class Node:
    def __init__(self, char, freq, left, right):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

def read_tree(string):
    global pos
    if string[pos] == "1":
        pos += 1
        char = chr(int(string[pos:pos+8], 2))
        pos += 8
        return Node(char, 0, None, None)
    pos += 1  # increment pos when we encounter "0"
    x = read_tree(string)
    y = read_tree(string)
    return Node("", 0, x, y)


if __name__ == "__main__":
    pos = 0  # reset global pos
    decode_pos = 0  # separate variable for decoding position
    TREE = "00001011101000101110101101101001100001010001011000110101110110010110011010110011110110010100000101101000101101100010111000010011001110110010010110000100101110010100100000001011011011011011100101101111101110011"
    COMPRESSED = "000110100001111000111001011010001100101011000111100011111011100010100101111111011111001100000011100001101110011110111110011110110100110011000101010011010000100110111111110111000111101000110100001000011110110010111011110010111101100011101110111000111101000001110010100101110100010011010101001101"
    root = read_tree(TREE)
    out = ""

    while decode_pos < len(COMPRESSED):
        x = root
        while x.left != None:
            if COMPRESSED[decode_pos] == "0":
                x = x.left
            else:
                x = x.right
            decode_pos += 1
        out += x.char
    print(out)
