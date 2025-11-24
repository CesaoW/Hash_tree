from base import *

class HashPage(Page):
    '''Hash Page - Bucket for Linear Hashing'''
    
    def __init__(self, size, data=None):
        super().__init__(size, data)
        self._overflow = None # ponteiro para o overflow
    
    def insert(self, record):
        '''Insert record into bucket'''
        key = record[0]
        
        # Verifica se a chave já existe
        if self.search(key):
            return False 
                
        if self.used_space + get_size(record) <= self._size:
            self._data.append(tuple(record))
            return True
        else:
            # cria página de overflow
            if self._overflow is None:
                self._overflow = HashPage(self._size)
            return self._overflow.insert(record)
    
    def remove(self, key):
        '''Remove record by key'''
        # Procura na página principal
        for i, record in enumerate(self._data):
            if record[0] == key:
                self._data.pop(i)
                return True
        
        # Procura nas páginas de overflow
        if self._overflow is not None:
            return self._overflow.remove(key)
        
        return False
    
    def search(self, key):
        '''Search for record by key'''
        # Procura na página principal
        for record in self._data:
            if record[0] == key:
                return [record]
        
        # Procura nas páginas de overflow
        if self._overflow is not None:
            return self._overflow.search(key)
        
        return []
    
    def get_all_records(self):
        '''Get all records including overflow pages'''
        records = list(self._data)
        if self._overflow is not None:
            records.extend(self._overflow.get_all_records())
        return records
    
    def has_overflow(self):
        '''Check if bucket has overflow pages'''
        return self._overflow is not None
    
    def count_overflow_pages(self):
        '''Count number of overflow pages'''
        if self._overflow is None:
            return 0
        return 1 + self._overflow.count_overflow_pages()
    
    def clear(self):
        '''Clear all data from bucket'''
        self._data = []
        self._overflow = None
    
    def __repr__(self):
        overflow_info = f" (+{self.count_overflow_pages()} overflow)" if self.has_overflow() else ""
        return f"[{len(self._data)} records{overflow_info}]"
    

class LinearHashIndex(Index):
    '''Linear Hashing Index'''
    
    def __init__(self, size, log, initial_buckets=4, utilization=0.8, debugging=False):
        super().__init__(size, log, debugging)
        
        self._utilization = utilization
        
        # Parâmetros do Linear Hashing
        self._level = 0  # Nível atual (d)
        self._next_split = 0  # Próximo bucket a ser dividido (sp)
        self._initial_buckets = initial_buckets
        self._num_buckets = initial_buckets  # Número inicial de buckets (2^d)
        
        # Inicializa buckets
        self._buckets = [HashPage(size) for _ in range(initial_buckets)]
        
        # Estatísticas
        self._num_records = 0
        self._num_splits = 0
        
        self._debug('Linear Hash index created:')
        self._debug('  Initial buckets: %s', initial_buckets)
        self._debug('  Utilization threshold: %.2f', utilization)
    
    def _hash(self, key, level):
        '''Hash function: h_level(key) = key % (2^level * initial_buckets)'''
        return key % (2 ** level * self._initial_buckets)
    
    def _get_bucket_index(self, key):
        '''Get bucket index for a key'''
        # Usa h_level(key)
        bucket_idx = self._hash(key, self._level)
        
        # Se o bucket já foi dividido, usa h_(level+1)(key)
        if bucket_idx < self._next_split:
            bucket_idx = self._hash(key, self._level + 1)
        
        return bucket_idx
    
    def _need_split(self):
        '''Check if split is needed based on load factor'''
        avg_occupancy = self._num_records / self._num_buckets
        max_records_per_bucket = self._size / get_size([0, 0, 0])  # Estimativa
        load_factor = avg_occupancy / max_records_per_bucket
        
        self._debug('  Load factor: %.3f (threshold: %.3f)', load_factor, self._utilization)
        
        return load_factor >= self._utilization
    
    def _split(self):
        '''Split the next bucket'''
        self._debug('Splitting bucket %d (level=%d)', self._next_split, self._level)
        self._num_splits += 1
        
        # Bucket a ser dividido
        old_bucket_idx = self._next_split
        old_bucket = self._buckets[old_bucket_idx]
        
        # Novo bucket
        new_bucket_idx = self._next_split + (2 ** self._level * self._initial_buckets)
        new_bucket = HashPage(self._size)
        self._buckets.append(new_bucket)
        self._num_buckets += 1
        
        # Redistribui registros
        records = old_bucket.get_all_records()
        old_bucket.clear()
        
        for record in records:
            key = record[0]
            # Usa h_(level+1) para determinar o bucket
            bucket_idx = self._hash(key, self._level + 1)
            
            if bucket_idx == old_bucket_idx:
                old_bucket.insert(record)
            else:
                new_bucket.insert(record)
        
        self._debug('  Records redistributed: %d -> bucket %d (%d) + bucket %d (%d)',
                   len(records), old_bucket_idx, len(old_bucket.get_all_records()),
                   new_bucket_idx, len(new_bucket.get_all_records()))
        
        # Atualiza next_split
        self._next_split += 1
        
        # Se completou um round, aumenta o level
        if self._next_split >= (2 ** self._level * self._initial_buckets):
            self._debug('  Completed round %d, incrementing level to %d', self._level, self._level + 1)
            self._level += 1
            self._next_split = 0
    
    def insert(self, record):
        '''Insert record into Linear Hash'''
        key = record[0]
        self._debug('Inserting record: %s', record)
        
        # Determina o bucket
        bucket_idx = self._get_bucket_index(key)
        self._debug('  Bucket index: %d', bucket_idx)
        
        # Insere no bucket
        if self._buckets[bucket_idx].insert(record):
            self._num_records += 1
            self._debug('  Record inserted successfully')
            
            # Verifica se precisa fazer split
            if self._need_split():
                self._debug('  Split triggered!')
                self._split()
            
            return True
        else:
            self._debug('  Record already exists (duplicate key)')
            return False
    
    def remove(self, key):
        '''Remove record from Linear Hash'''
        self._debug('Removing key: %s', key)
        
        # Determina o bucket
        bucket_idx = self._get_bucket_index(key)
        self._debug('  Bucket index: %d', bucket_idx)
        
        # Remove do bucket
        if self._buckets[bucket_idx].remove(key):
            self._num_records -= 1
            self._debug('  Record removed successfully')
            return True
        else:
            self._debug('  Key not found')
            return False
    
    def search(self, key):
        '''Search for record in Linear Hash'''
        self._debug('Searching for key: %s', key)
        
        # Determina o bucket
        bucket_idx = self._get_bucket_index(key)
        self._debug('  Bucket index: %d', bucket_idx)
        
        # Busca no bucket
        result = self._buckets[bucket_idx].search(key)
        
        if result:
            self._debug('  Record found: %s', result)
        else:
            self._debug('  Key not found')
        
        return result
    
    def get_statistics(self):
        '''Get index statistics'''
        total_overflow = sum(bucket.count_overflow_pages() for bucket in self._buckets)
        buckets_with_overflow = sum(1 for bucket in self._buckets if bucket.has_overflow())
        
        return {
            'num_buckets': self._num_buckets,
            'num_records': self._num_records,
            'level': self._level,
            'next_split': self._next_split,
            'num_splits': self._num_splits,
            'overflow_pages': total_overflow,
            'buckets_with_overflow': buckets_with_overflow,
            'avg_records_per_bucket': self._num_records / self._num_buckets if self._num_buckets > 0 else 0
        }
    
    def __repr__(self):
        '''String representation of Linear Hash'''
        stats = self.get_statistics()
        
        result = "\n=== Linear Hash Structure ===\n"
        result += f"Level (d): {stats['level']}\n"
        result += f"Next Split (sp): {stats['next_split']}\n"
        result += f"Number of buckets: {stats['num_buckets']}\n"
        result += f"Number of records: {stats['num_records']}\n"
        result += f"Avg records/bucket: {stats['avg_records_per_bucket']:.2f}\n"
        result += f"Total splits: {stats['num_splits']}\n"
        result += f"Overflow pages: {stats['overflow_pages']}\n"
        result += f"Buckets with overflow: {stats['buckets_with_overflow']}\n"
        result += "\nBuckets:\n"
        
        for i, bucket in enumerate(self._buckets):
            records = bucket.get_all_records()
            keys = [r[0] for r in records]
            overflow_marker = " *" if bucket.has_overflow() else ""
            
            if i == self._next_split:
                result += f"  -> Bucket {i:3d}: {keys}{overflow_marker} (next to split)\n"
            else:
                result += f"     Bucket {i:3d}: {keys}{overflow_marker}\n"
        
        return result
