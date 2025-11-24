# -*- coding: utf-8 -*-

from base import *

class TreePage(Page):
    '''Tree Page - Base class for tree nodes'''
    
    def __init__(self, size, data=None):
        super().__init__(size, data)
    
    def _repr_(self):
        '''String representation'''
        return str(self._data)
    
    def binary_search(self, key, begin=0):
        '''Binary search on keys'''
        L = self.get_key_list()
        end = len(L)
        
        while begin < end:
            h = (begin + end) // 2  
            
            if key < L[h]:
                end = h
            else:
                begin = h + 1
        
        return begin
    
    def get_key(self, position):
        '''Get key at position'''
        raise NotImplementedError
    
    def get_key_list(self):
        '''Get list of keys'''
        raise NotImplementedError
    
    def split(self):
        '''Split page'''
        raise NotImplementedError

class LeafPage(TreePage):
    '''Leaf Page - Contains records ordered by key'''
    
    def __init__(self, size, data=None):
        super().__init__(size, data)
    
    def get_key(self, position):
        '''Get key at position'''
        if 0 <= position < len(self._data):
            return self._data[position][0]
        return None
    
    def get_key_list(self):
        '''Get list of all keys'''
        return [record[0] for record in self._data]
    
    def get_left(self, remove):
        '''Get left sibling (not used in leaf)'''
        return None
    
    def get_right(self, remove):
        '''Get right sibling (not used in leaf)'''
        return None
    
    def get_structure(self, level=0):
        '''Get structure for visualization'''
        indent = "  " * level
        result = f"{indent}LeafPage: {self.get_key_list()}\n"
        return result
    
    def insert(self, record):
        '''Insert record maintaining order'''
        key = record[0]
        position = self.binary_search(key)
        self._data.insert(position, tuple(record))
        return True
    
    def remove(self, key):
        '''Remove record by key'''
        for i, record in enumerate(self._data):
            if record[0] == key:
                self._data.pop(i)
                return True
        return False
    
    def search(self, key):
        '''Search for record by key'''
        result = []
        for record in self._data:
            if record[0] == key:
                result.append(record)
        return result
    
    def split(self):
        '''Split leaf page into two'''
        mid = len(self._data) // 2
        new_page = LeafPage(self._size)
        new_page.set_data(self._data[mid:])
        self._data = self._data[:mid]
        return new_page
    
class NonLeafPage(TreePage):
    '''Non-Leaf Page - Internal node with keys and pointers'''
    
    def __init__(self, size, data=None):
        super().__init__(size, data)
        # data armazena alternadamente: [filho0, chave0, filho1, chave1, ..., filhoN]
        # Posições pares são filhos, ímpares são chaves
    
    def _borrow_sibling(self, child_pos):
        '''Verifica qual irmão tem melhores condições de emprestar'''
        # Retorna o índice do irmão (esquerda ou direita)
        left_sibling = child_pos - 2 if child_pos >= 2 else None
        right_sibling = child_pos + 2 if child_pos + 2 < len(self._data) else None
        
        if left_sibling is not None and right_sibling is not None:
            if len(self._data[left_sibling]) > len(self._data[right_sibling]):
                return left_sibling
            return right_sibling
        elif left_sibling is not None:
            return left_sibling
        elif right_sibling is not None:
            return right_sibling
        return None
    
    def _join_child(self, pos, child):
        '''Tenta juntar o filho (child) com irmãos'''
        sibling_pos = self._borrow_sibling(pos)
        if sibling_pos is not None:
            pass
        return child
    
    def binary_search(self, key, begin=0):
        '''Binary search considering only keys (odd positions)'''
        key_list = self.get_key_list()
        end = len(key_list)
        
        while begin < end:
            h = (begin + end) // 2
            if key < key_list[h]:
                end = h
            else:
                begin = h + 1
        
        return begin * 2
    
    def get_key(self, position):
        '''Get key at position (position in key indices)'''
        key_pos = position * 2 + 1
        if key_pos < len(self._data):
            return self._data[key_pos]
        return None
    
    def get_key_list(self):
        '''Get list of keys (odd positions)'''
        return [self._data[i] for i in range(1, len(self._data), 2)]
    
    def get_left(self, remove):
        '''Get left child based on condition'''
        return self._data[0] if len(self._data) > 0 else None
    
    def get_right(self, remove):
        '''Get right child based on condition'''
        return self._data[-1] if len(self._data) > 0 else None
    
    def get_structure(self, level=0):
        '''Get structure for visualization (recursive)'''
        indent = "  " * level
        result = f"{indent}NonLeafPage: Keys={self.get_key_list()}\n"
        
        for i in range(0, len(self._data), 2):
            child = self._data[i]
            if isinstance(child, TreePage):
                result += child.get_structure(level + 1)
        
        return result
    
    def insert(self, record):
        '''Insert record recursively'''
        key = record[0]
        child_pos = self.binary_search(key)
        
        if child_pos < len(self._data):
            child = self._data[child_pos]
            child.insert(record)
            
            if child.used_space > child._size:
                self._split_child(child_pos)
        
        return True
    
    def _split_child(self, child_pos):
        '''Split a child and update current node'''
        child = self._data[child_pos]
        new_child = child.split()
        
        if isinstance(child, LeafPage):
            new_key = new_child.get_key(0)
        else:
            new_key = new_child.get_key_list()[0]
        
        self._data.insert(child_pos + 1, new_key)
        self._data.insert(child_pos + 2, new_child)
    
    def remove(self, key):
        '''Remove record recursively'''
        child_pos = self.binary_search(key)
        
        if child_pos < len(self._data):
            child = self._data[child_pos]
            result = child.remove(key)
            
            # Verifica se precisa rebalancear            
            return result
        
        return False
    
    def search(self, key):
        '''Search recursively'''
        child_pos = self.binary_search(key)
        
        if child_pos < len(self._data):
            child = self._data[child_pos]
            return child.search(key)
        
        return []
    
    def split(self):
        '''Split non-leaf page'''
        mid = len(self._data) // 2
        # Garante que mid seja par (posição de filho)
        if mid % 2 == 1:
            mid -= 1
        
        new_page = NonLeafPage(self._size)
        new_page.set_data(self._data[mid:])
        self._data = self._data[:mid]
        
        return new_page

class BTreeIndex():
    '''B-Tree Index'''
    
    def __init__(self, size, log, debugging=False):
        self._size = size
        self._debugging = debugging
        self._root = LeafPage(size)  # Raiz começa como LeafPage
        
        self._config_log(log)
        self._debug('Creating BTree index with page size = %s', size)
    
    def insert(self, record):
        '''Insert record into B-Tree'''
        self._debug('Inserting record: %s', record)
        
        self._root.insert(record)
        
        # Verifica se a raiz precisa ser dividida
        if self._root.used_space > self._size:
            self._debug('Root needs to be split')
            old_root = self._root
            new_sibling = old_root.split()
            
            # Cria nova raiz
            self._root = NonLeafPage(self._size)
            
            # Adiciona filhos e chave separadora
            if isinstance(old_root, LeafPage):
                separator_key = new_sibling.get_key(0)
            else:
                separator_key = new_sibling.get_key_list()[0]
            
            self._root.set_data([old_root, separator_key, new_sibling])
        
        return True
    
    def remove(self, key):
        '''Remove record from B-Tree'''
        self._debug('Removing key: %s', key)
        result = self._root.remove(key)
        
        # Se a raiz for NonLeafPage e tiver apenas 1 filho, substitui pela raiz
        if isinstance(self._root, NonLeafPage) and len(self._root.data) == 1:
            self._root = self._root.data[0]
        
        return result
    
    def search(self, key):
        '''Search for record in B-Tree'''
        self._debug('Searching for key: %s', key)
        return self._root.search(key)
    
    def range_search(self, min_key, max_key):
        '''Search for all records in range [min_key, max_key]'''
        self._debug('Range search: [%s, %s]', min_key, max_key)
        results = []
        self._range_search_helper(self._root, min_key, max_key, results)
        return results
    
    def _range_search_helper(self, node, min_key, max_key, results):
        '''Helper function for range search'''
        if isinstance(node, LeafPage):
            # Leaf node: collect records in range
            for record in node.data:
                if min_key <= record[0] <= max_key:
                    results.append(record)
        else:
            # Non-leaf node: recursively search children
            for i in range(0, len(node.data), 2):
                child = node.data[i]
                self._range_search_helper(child, min_key, max_key, results)
    
    def get_statistics(self):
        '''Get B-Tree statistics'''
        stats = {
            'height': self._get_height(self._root),
            'num_nodes': self._count_nodes(self._root),
            'num_leaf_nodes': self._count_leaf_nodes(self._root),
            'num_records': self._count_records(self._root)
        }
        return stats
    
    def _get_height(self, node):
        '''Calculate tree height'''
        if isinstance(node, LeafPage):
            return 1
        max_height = 0
        for i in range(0, len(node.data), 2):
            child = node.data[i]
            max_height = max(max_height, self._get_height(child))
        return 1 + max_height
    
    def _count_nodes(self, node):
        '''Count total number of nodes'''
        if isinstance(node, LeafPage):
            return 1
        count = 1
        for i in range(0, len(node.data), 2):
            child = node.data[i]
            count += self._count_nodes(child)
        return count
    
    def _count_leaf_nodes(self, node):
        '''Count number of leaf nodes'''
        if isinstance(node, LeafPage):
            return 1
        count = 0
        for i in range(0, len(node.data), 2):
            child = node.data[i]
            count += self._count_leaf_nodes(child)
        return count
    
    def _count_records(self, node):
        '''Count total number of records'''
        if isinstance(node, LeafPage):
            return len(node.data)
        count = 0
        for i in range(0, len(node.data), 2):
            child = node.data[i]
            count += self._count_records(child)
        return count
    
    def load_file(self, filename):
        '''Load CSV file'''
        with open(filename, encoding='utf-8') as arq:
            reader = csv.reader(arq)
            next(reader)  # Skip header
            
            for position, line in enumerate(reader):
                # Skip empty lines
                if not line or len(line) == 0:
                    self._debug('Line %s: Empty line, skipping', position)
                    continue
                
                self._debug('Line %s: %s', position, line)
                operation = line[0]
                
                # Skip lines with only operation and no data
                if len(line) < 2:
                    self._debug('Line %s: No data after operation, skipping', position)
                    continue
                
                record = [int(value) for value in line[1:]]
                
                if operation == "+":
                    self.insert(record)
                elif operation == "-":
                    self.remove(record[0])
                elif operation == "?":
                    result = self.search(record[0])
                    if result:
                        self._log.info('Key %s found: %s', record[0], result)
                    else:
                        self._log.info('Key %s not found', record[0])
                
                self._debug(str(self))
    
    def __repr__(self):
        '''String representation of B-Tree'''
        return f"\n=== B-Tree Structure ===\n{self._root.get_structure()}"
    
    def __str__(self):
        return self.__repr__()
    
    def _debug(self, msg, *args, **kwargs):
        self._log.debug(msg, *args, **kwargs)
    
    def _config_log(self, log):
        '''Configure logging'''
        self._log = logging.getLogger(log)
        str_format = '%(levelname)s - %(message)s'
        log_format = logging.Formatter(str_format)
        
        file_handler = logging.FileHandler(log)      
        file_handler.setFormatter(log_format)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        
        self._log.addHandler(file_handler)
        self._log.addHandler(console_handler)
        
        if self._debugging:
            self._log.setLevel(logging.DEBUG)
        else:
            self._log.setLevel(logging.INFO)
    
    def menu(self):
        '''Menu for interactive execution'''
        while True:
            print(str(self))
            print('+ key val1 val2... | - key | ? key | (Q)uit')
            resp = input().lower().strip()
            
            if resp == 'q':
                break
            elif resp[0] == '+':
                record = resp[1:].split()
                if len(record) > 0:
                    record = [int(value) for value in record]
                    self.insert(record)
            elif resp[0] == '-':
                key = resp[1:].strip()
                if len(key) > 0:
                    key = int(key)
                    self.remove(key)
            elif resp[0] == '?':
                key = resp[1:].strip()
                if len(key) > 0:
                    key = int(key)
                    record_list = self.search(key)
                    if len(record_list) == 0:
                        print('Key not found!')
                    else:
                        print('Records found:')
                        for record in record_list:
                            print(record)
            else:
                try:
                    key = int(resp)
                    record_list = self.search(key)
                    if len(record_list) == 0:
                        print('Key not found!')
                    else:
                        print('Records found:')
                        for record in record_list:
                            print(record)
                except ValueError:
                    print('Invalid input!')