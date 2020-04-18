from bitarray import bitarray


class Node:
    def __init__(self, weight=1, letter='', left=None, right=None, parent=None):
        self.weight = weight
        self.letter = letter
        self.left = left
        self.right = right
        self.parent = parent
        self.id = None

    def __lt__(self, other):
        return self.weight < other.weight

    def __eq__(self, other):
        return id(self) == id(other)

    def __repr__(self):
        return f'letter: {self.letter} weight: {self.weight} id: {id(self)}'


class DHuffman:
    def __init__(self, text=None, file=False):
        self.dictionary = {}
        self.tree = None
        self.text = text
        self.from_file = file
        self.weights = [None]*256
        self.weight_pointers = {}

    def encode_letter(self, letter_node):
        code = ""
        prev = letter_node
        curr = letter_node.parent
        while curr is not None:
            if curr.left == prev:
                code = "1" + code
            else:
                code = "0" + code
            prev = prev.parent
            curr = curr.parent
        return code

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

    def swap(self, node1, node2):
        if node1.parent.left == node1 and node2.parent.left == node2:
            node1.parent.left, node2.parent.left = node2, node1
        elif node1.parent.right == node1 and node2.parent.left == node2:
            node1.parent.right, node2.parent.left = node2, node1
        elif node1.parent.right == node1 and node2.parent.right == node2:
            node1.parent.right, node2.parent.right = node2, node1
        elif node1.parent.left == node1 and node2.parent.right == node2:
            node1.parent.left, node2.parent.right = node2, node1

        node1.parent, node2.parent = node2.parent, node1.parent
        self.weights[node1.id], self.weights[node2.id] = node2, node1
        node1.id, node2.id = node2.id, node1.id

    def get_greatest_of_weight(self, ptr):
        w = ptr.weight
        i = ptr.id
        gw = self.weight_pointers[w]
        if gw == i and self.weights[i-1].weight != w:
            del self.weight_pointers[w]
        else:
            self.weight_pointers[w] -= 1
        if w+1 not in self.weight_pointers.keys():
            self.weight_pointers[w+1] = gw
        return self.weights[gw]

    def build_tree_compress(self, data):
        self.tree = Node(weight=0, letter='#_')
        nodes = {'#_': self.tree}
        self.tree.id = 255
        self.weights[255] = self.tree
        self.weight_pointers[0] = 255
        code = ""
        curr_id = 254
        for letter in data:
            if letter in nodes.keys():
                # first encode letter with old tree
                code += self.encode_letter(nodes[letter])
                # then prepare for the tree update
                ptr = nodes[letter]
            else:
                # first encode letter with old tree
                letter_code = self.encode_letter(nodes['#_'])
                letter_code += self.letter_fixed_code(letter)
                code += letter_code
                # then update the tree
                node = Node(weight=1, letter=letter, parent=nodes['#_'])
                nodes['#_'].letter = ''
                nodes['#_'].weight += 1

                if 1 not in self.weight_pointers.keys():
                    self.weight_pointers[1] = nodes['#_'].id

                nodes['#_'].left = Node(weight=0, letter='#_', parent=nodes['#_'])
                nodes['#_'].right = node
                nodes['#_'] = nodes['#_'].left

                nodes[letter] = node
                nodes[letter].id = curr_id
                self.weights[curr_id] = nodes[letter]
                nodes['#_'].id = curr_id-1
                self.weight_pointers[0] = curr_id-1
                self.weights[curr_id-1] = nodes['#_']
                curr_id -= 2

                ptr = nodes['#_'].parent.parent

            while ptr is not None:
                block_greatest = self.get_greatest_of_weight(ptr)
                if not ptr == block_greatest and not block_greatest == ptr.parent:
                    self.swap(ptr, block_greatest)

                ptr.weight += 1
                ptr = ptr.parent
        return code

    def compress(self, path="dh_compressed"):
        self.weights = [None] * 256
        self.weight_pointers = {}
        if self.from_file:
            with open(self.text, "r") as f:
                data = f.read()
        else:
            data = self.text
        line = self.build_tree_compress(data)
        line = '0'*((8 - len(line) % 8) - 1) + '1' + line #for length divisible by 8 extra 8 bits will be added

        with open(path, "wb") as f:
            binary_format = bitarray(line)
            f.write(binary_format.tobytes())

    def fixed_code_to_letter(self, data):
        if len(data) == 0:
            return ""
        data_ = ''.join('0' if b else '1' for b in data)
        return chr(int(data_, 2))

    def build_tree_decompress(self, code):
        self.tree = Node(weight=0, letter='#_')
        nodes = {'#_': self.tree}
        data = ""
        self.tree.id = 255
        self.weights = [None]*256
        self.weights[255] = self.tree
        self.weight_pointers = {0: 255}
        curr_id = 254
        i = 0
        while i < len(code):
            letter = None
            j = 0
            ptr = self.tree
            while i + j < len(code)+1:
                if ptr.letter == '#_':
                    break
                elif ptr.letter != '':
                    letter = ptr.letter
                    break

                if code[i+j]:
                    ptr = ptr.left
                else:
                    ptr = ptr.right
                j += 1

            if letter:
                # first add letter then output
                data += letter
                # then prepare for th tree update
                ptr = nodes[letter]

            else:
                # first encode letter with old tree
                letter = self.fixed_code_to_letter(code[i+j:i+j+8])
                data += letter
                # then update the tree
                node = Node(weight=1, letter=letter, parent=nodes['#_'])
                nodes['#_'].letter = ''
                nodes['#_'].weight += 1

                if 1 not in self.weight_pointers.keys():
                    self.weight_pointers[1] = nodes['#_'].id

                nodes['#_'].left = Node(weight=0, letter='#_', parent=nodes['#_'])
                nodes['#_'].right = node
                nodes['#_'] = nodes['#_'].left

                nodes[letter] = node
                nodes[letter].id = curr_id
                self.weights[curr_id] = nodes[letter]
                nodes['#_'].id = curr_id-1
                self.weight_pointers[0] = curr_id-1
                self.weights[curr_id-1] = nodes['#_']
                curr_id -= 2
                i += 8
                ptr = nodes['#_'].parent.parent

            while ptr is not None:
                block_greatest = self.get_greatest_of_weight(ptr)
                if not ptr == block_greatest and not block_greatest == ptr.parent:
                    self.swap(ptr, block_greatest)

                ptr.weight += 1
                ptr = ptr.parent
            i += j
        return data

    def decompress(self, path_in="dh_compressed", path_out="dh_decompressed.txt"):
        with open(path_in, "rb") as f:
            data_bytes = f.read()
        binary_format = bitarray()
        binary_format.frombytes(data_bytes)
        data = binary_format.tolist()
        i = 0
        while not data[i]:
            i += 1

        line = self.build_tree_decompress(data[i+1:])
        with open(path_out, "w") as f:
            f.write(line)


if __name__ == '__main__':
    s = DHuffman("data/1000B", file=True)
    s.compress()
    s = DHuffman()
    s.decompress()


