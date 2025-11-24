# -*- coding: utf-8 -*-

# importação bibliotecas 
import csv 
import logging 
import argparse

PAGE_SIZE = 512 


def get_size(data):
    '''Get size of data'''
    if isinstance(data, list):
        return sum(item.__sizeof__() for item in data)
    
    return data.__sizeof__()


# classe pagina 
class Page():
    '''Data Page'''
    def __init__(self, size, data=None):
        self._size = size
        self._data = []
        if data is not None:
            self._data = data
    
    @property
    def used_space(self):
        '''Used space of page'''
        return get_size(self._data)
    
    def insert(self, record):
        '''Insert record'''
        raise NotImplementedError

    def remove(self, key):
        '''Remove record by a key'''
        raise NotImplementedError
    
    @property
    def data(self):
        '''Page data'''
        return self._data
    
    def set_data(self, data):
        '''Set page data'''
        self._data = data

    def search(self, key):
        '''Search for record'''
        raise NotImplementedError

    def __len__(self):
        return len(self._data)
    

class Index():
    '''
    Hashing Index
    '''

    def __init__(self, size, log, debugging=False):
        self._size = size
        # debug
        self._debugging = debugging
        
        self._config_log(log)
        self._debug('Creating index page = %s', size)

    def insert(self, record):
        '''Insert record'''
        raise NotImplementedError

    def remove(self, key):
        '''Remove record'''
        raise NotImplementedError

    def search(self, key):
        '''Search for record'''
        raise NotImplementedError

    def load_file(self, filename):
        '''Load CSV file'''
    
        # Open and load CSV file
        with open(filename, encoding='utf-8') as arq:

            reader = csv.reader(arq)
            # Skip header
            next(reader)
            # For each file 
            for position, line in enumerate(reader):
                # Skip empty lines
                if not line or len(line) == 0:
                    self._debug('Line %s: Empty line, skipping', position)
                    continue
                
                self._debug('Line %s: %s', position, line)
                
                # Skip lines with only operation and no data
                if len(line) < 2:
                    self._debug('Line %s: No data after operation, skipping', position)
                    continue
                
                # get operation (+, - or ?)
                operation = line[0]
                record = [int(value) for value in line[1:]]
                # perform operation
                if operation == "+":
                    self.insert(record)
                elif operation == "-":
                    self.remove(record[0])
                elif operation == "?":
                    self.search(record[0])
                self._debug(str(self))

    def __repr__(self):
        # Representation of str()
        raise NotImplementedError

    def _debug(self, msg, *args, **kwargs):
        self._log.debug(msg, *args, **kwargs)

    def _config_log(self, log):
        # Create log
        self._log = logging.getLogger(log)
        # Message Format
        str_format = '%(levelname)s - %(message)s'
        log_format = logging.Formatter(str_format)
        # log file 
        file_handler = logging.FileHandler(log)      
        file_handler.setFormatter(log_format)
        # console log 
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        self._log.addHandler(file_handler)
        self._log.addHandler(console_handler)
        # Check if debug is activated
        if self._debugging:
            self._log.setLevel(logging.DEBUG)
        else:
            self._log.setLevel(logging.INFO)

    def menu(self):
        '''
        Menu for interactive execution
        '''
        while True:
            print(str(self))
            print('+ | - | key | (Q)uit')
            resp = input().lower().strip()

            if resp[0] == '+':
                record = resp[1:].split()
                if len(record) > 0:
                    record = [int(value) for value in record]
                    record = tuple(record)
                    self.insert(record)

            elif resp[0] == '-':
                key = resp[1:].strip()
                if len(key) > 0:
                    key = int(key)
                    self.remove(key)

            elif resp == 'q':
                break

            else:
                key = int(resp)
                record_list = self.search(key)

                if len(record_list) == 0:
                    print('Key not found!')
                else:
                    print('Records found:')
                    for record in record_list:
                        print(record)
                        input()


def get_arguments(text):
    '''Get Arguments'''
    
    parser = argparse.ArgumentParser(text)
    parser.add_argument('-f', '--file', help='Input file (CSV)')
    parser.add_argument('-p', '--page-size', type=int, default=PAGE_SIZE)
    parser.add_argument('-D', '--debug', action="store_true", 
                                default=False, help='Debug Execution')
    args = parser.parse_args()
    return args
