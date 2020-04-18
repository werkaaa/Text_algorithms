from collections import Counter
from bitarray import bitarray


class Node:
    def __init__(self, weight, letter='', left=None, right=None):
        self.weight = weight
        self.letter = letter
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.weight < other.weight

    def __repr__(self):
        return f'letter: {self.letter} weight: {self.weight}'


class SHuffman:
    def __init__(self, text=None, file=False):
        if text:
            if file:
                with open(text, "r") as f:
                    data = f.read()
                    self.letter_counts = Counter(data)
            else:
                self.letter_counts = Counter(text)
        else:
            self.letter_counts = {}

        self.dictionary = {}
        self.tree = None
        self.text = text
        self.from_file = file
        self.tree_code = ''
        self.letter_number = len(self.letter_counts)
        self.letter_cnt = 0

    def build_tree(self):
        nodes = [Node(w, l) for (l, w) in self.letter_counts.items()]
        internal_nodes = []
        leafs = sorted(nodes)

        while len(leafs) + len(internal_nodes) > 1:
            head = []
            head += internal_nodes[:min(2, len(internal_nodes))]
            head += leafs[:min(2, len(leafs))]
            elem1, elem2 = sorted(head)[:2]
            internal_nodes.append(Node(elem1.weight + elem2.weight, left=elem1, right=elem2))
            if len(leafs) and leafs[0] == elem1:
                leafs = leafs[1:]
            else:
                internal_nodes = internal_nodes[1:]

            if len(leafs) and leafs[0] == elem2:
                leafs = leafs[1:]
            else:
                internal_nodes = internal_nodes[1:]

        self.tree = internal_nodes[0]

    def _build_dict(self, node, code):
        if node.letter != '':
            self.dictionary[node.letter] = code
        else:
            self._build_dict(node.left, code + '1')
            self._build_dict(node.right, code + '0')

    def build_dict(self):
        self._build_dict(self.tree, "")

    def letter_fixed_code(self, letter):
        array = bitarray()
        array.fromstring(letter)
        data_ = array.tolist()
        data = ""
        for b in data_:
            if b:
                data += "0"
            else:
                data += "1"
        return data

    def build_string_from_tree(self, node):
        if node is None:
            return
        if node.left.letter == '':
            self.tree_code += '0'
            self.build_string_from_tree(node.left)
        else:
            self.tree_code += '1'
            self.tree_code += self.letter_fixed_code(node.left.letter)

        if node.right.letter == '':
            self.tree_code += '0'
            self.build_string_from_tree(node.right)
        else:
            self.tree_code += '1'
            self.tree_code += self.letter_fixed_code(node.right.letter)

    def fixed_code_to_letter(self, data):
        if len(data) == 0:
            return ""
        data_ = ''.join('0' if b else '1' for b in data)
        return chr(int(data_, 2))

    def build_tree_from_string(self, node):
        if self.letter_cnt == self.letter_number:
            return
        if self.tree_code[0]:
            node.left = Node(weight=0, letter=self.fixed_code_to_letter(self.tree_code[1:9]))
            self.tree_code = self.tree_code[9:]
            self.letter_cnt += 1
        else:
            node.left = Node(weight=0, letter='')
            self.tree_code = self.tree_code[1:]
            self.build_tree_from_string(node.left)

        if self.tree_code[0]:
            node.right = Node(weight=0, letter=self.fixed_code_to_letter(self.tree_code[1:9]))
            self.tree_code = self.tree_code[9:]
            self.letter_cnt += 1
        else:
            node.right = Node(weight=0, letter='')
            self.tree_code = self.tree_code[1:]
            self.build_tree_from_string(node.right)

    def compress(self, path="sh_compressed"):
        self.build_tree()
        self.build_dict()
        line = ''
        self.tree_code = ''
        if self.from_file:
            with open(self.text, "r") as f:
                data = f.read()
        else:
            data = self.text

        for letter in data:
            line += self.dictionary[letter]

        self.build_string_from_tree(self.tree)
        number_code = bin(255 - self.letter_number)[2:]
        while len(number_code) < 8:
            number_code = '0' + number_code
        line = number_code + self.tree_code + line
        line = '0'*((8 - len(line) % 8) - 1) + '1' + line

        with open(path, "wb") as f:
            binary_format = bitarray(line)
            f.write(binary_format.tobytes())

    def decompress(self, path_in="sh_compressed", path_out="sh_decompressed.txt"):
        self.letter_cnt = 0
        with open(path_in, "rb") as f:
            data_bytes = f.read()
        binary_format = bitarray()
        binary_format.frombytes(data_bytes)
        data = binary_format.tolist()
        i = 0
        while not data[i]:
            i += 1
        i += 1
        self.letter_number = ord(self.fixed_code_to_letter(data[i:i+8]))
        self.tree_code = data[i+8:]
        self.tree = Node(weight=0, letter = '')
        self.build_tree_from_string(self.tree)
        data = self.tree_code

        line = ""
        node = self.tree
        # one-line text
        if node.letter != '':
            line += node.letter
            node = self.tree

        for bit in data:
            if bit:
                node = node.left
            else:
                node = node.right
            if node.letter != '':
                line += node.letter
                node = self.tree

        with open(path_out, "w") as f:
            f.write(line)


if __name__ == '__main__':
    s = SHuffman("data/1000B", file=True)
    s = SHuffman()
    s.compress()
    s.decompress()


