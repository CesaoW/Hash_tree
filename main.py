# -*- coding: utf-8 -*-

"""
B-Tree e Linear Hashing
Compatível com SIOgen (https://ribeiromarcos.github.io/siogen/)
"""

import argparse
import time
import sys
from btree import *
from linear_hash import *


def get_arguments():
    '''Get command line arguments'''
    parser = argparse.ArgumentParser(
        description='Index Structures Implementation - B-Tree and Linear Hashing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # B-Tree interativo
  python main.py -t btree
  
  # B-Tree com arquivo SIOgen
  python main.py -t btree -f data.csv -p 512 -D
  
  # Linear Hash interativo
  python main.py -t linear
  
  # Linear Hash com arquivo SIOgen
  python main.py -t linear -f data.csv -p 512 -b 4 -u 0.8 -D
  
  # Busca por intervalo (apenas B-Tree)
  python main.py -t btree -f data.csv --range 10 50

SIOgen Format (CSV):
  operation,key,attr2,attr3,...
  +,10,100,200
  +,25,150,250
  -,10
  ?,25
        ''')
    
    # Argumentos obrigatórios
    parser.add_argument('-t', '--type', 
                        required=True,
                        choices=['btree', 'linear', 'b', 'l'],
                        help='Index type: btree/b (B-Tree) or linear/l (Linear Hash)')
    
    # Argumentos comuns
    parser.add_argument('-f', '--file', 
                        help='Input CSV file (SIOgen format)')
    parser.add_argument('-p', '--page-size', 
                        type=int, 
                        default=512,
                        help='Page size in bytes (default: 512, min: 256)')
    parser.add_argument('-D', '--debug', 
                        action="store_true",
                        default=False, 
                        help='Enable debug mode with detailed logging')
    
    # Argumentos específicos do Linear Hash
    parser.add_argument('-b', '--buckets', 
                        type=int, 
                        default=4,
                        help='[Linear Hash] Initial number of buckets (default: 4)')
    parser.add_argument('-u', '--utilization', 
                        type=float, 
                        default=0.8,
                        help='[Linear Hash] Load factor threshold (0.0-1.0, default: 0.8)')
    
    # Busca por intervalo (apenas B-Tree)
    parser.add_argument('--range', 
                        nargs=2, 
                        type=int, 
                        metavar=('MIN', 'MAX'),
                        help='[B-Tree] Perform range search after loading file')
    
    # Estatísticas e performance
    parser.add_argument('-s', '--stats', 
                        action="store_true",
                        help='Show detailed statistics after operations')
    
    args = parser.parse_args()
    
    # Validações
    if args.page_size < 256:
        parser.error('Page size must be at least 256 bytes')
    
    if args.utilization <= 0 or args.utilization > 1:
        parser.error('Utilization must be between 0.0 and 1.0')
    
    if args.range and args.type in ['linear', 'l']:
        parser.error('Range search is only supported for B-Tree')
    
    return args


def print_header(title):
    '''Print formatted header'''
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_config(config_dict):
    '''Print configuration parameters'''
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
    print("="*70 + "\n")


def run_btree(args):
    '''Execute B-Tree index'''
    print_header("B-TREE INDEX")
    
    config = {
        'Page size': f'{args.page_size} bytes',
        'Debug mode': 'ON' if args.debug else 'OFF',
    }
    
    if args.file:
        config['Input file'] = args.file
    if args.range:
        config['Range search'] = f'[{args.range[0]}, {args.range[1]}]'
    
    print_config(config)
    
    # Cria índice B-Tree
    start_time = time.time()
    btree = BTreeIndex(args.page_size, 'btree.log', debugging=args.debug)
    
    if args.file:
        print("Loading file...\n")
        btree.load_file(args.file)
        load_time = time.time() - start_time
        
        print("\n" + str(btree))
        
        # Busca por intervalo
        if args.range:
            print(f"\n{'='*70}")
            print(f"  RANGE SEARCH: [{args.range[0]}, {args.range[1]}]")
            print(f"{'='*70}")
            
            range_start = time.time()
            results = btree.range_search(args.range[0], args.range[1])
            range_time = time.time() - range_start
            
            print(f"\nFound {len(results)} records:")
            for record in results[:10]:  # Mostra no máximo 10
                print(f"  {record}")
            if len(results) > 10:
                print(f"  ... and {len(results) - 10} more records")
            
            print(f"\nRange search time: {range_time:.4f} seconds")
        
        # Estatísticas
        if args.stats:
            print(f"\n{'='*70}")
            print("  STATISTICS")
            print(f"{'='*70}")
            stats = btree.get_statistics()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print(f"  Load time: {load_time:.4f} seconds")
        
        print("\n✓ File processed successfully!")
    else:
        print("Interactive mode - Use the menu below:\n")
        btree.menu()


def run_linear_hash(args):
    '''Execute Linear Hashing index'''
    print_header("LINEAR HASHING INDEX")
    
    config = {
        'Page size': f'{args.page_size} bytes',
        'Initial buckets': args.buckets,
        'Utilization threshold': f'{args.utilization:.2f}',
        'Debug mode': 'ON' if args.debug else 'OFF',
    }
    
    if args.file:
        config['Input file'] = args.file
    
    print_config(config)
    
    # Cria índice Linear Hash
    start_time = time.time()
    lh = LinearHashIndex(
        args.page_size, 
        'linear_hash.log',
        initial_buckets=args.buckets,
        utilization=args.utilization,
        debugging=args.debug
    )
    
    if args.file:
        print("Loading file...\n")
        lh.load_file(args.file)
        load_time = time.time() - start_time
        
        print("\n" + str(lh))
        
        # Estatísticas
        if args.stats:
            print(f"\n{'='*70}")
            print("  STATISTICS")
            print(f"{'='*70}")
            stats = lh.get_statistics()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print(f"  Load time: {load_time:.4f} seconds")
        
        print("\n✓ File processed successfully!")
    else:
        print("Interactive mode - Use the menu below:\n")
        lh.menu()


def main():
    '''Main function'''
    try:
        args = get_arguments()
    except SystemExit as e:
        return e.code
    
    # Normaliza o tipo
    index_type = args.type.lower()
    
    try:
        if index_type in ['btree', 'b']:
            run_btree(args)
        elif index_type in ['linear', 'l']:
            run_linear_hash(args)
        else:
            print(f"Error: Unknown index type '{args.type}'")
            print("Use: btree, b, linear, or l")
            return 1
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: File not found - {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n✗ Execution interrupted by user.")
        return 0
    except Exception as e:
        print(f"\n✗ Error during execution: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

import matplotlib.pyplot as plt

# Seus dados exatos
registros = [1000, 10000, 50000]
tempo_bplus = [0.0120, 0.0144, 0.0259]
tempo_hash = [0.0011, 0.0035, 0.0199]

plt.figure(figsize=(10, 6))

# Linha da Árvore B+ (Vermelho)
plt.plot(registros, tempo_bplus, marker='o', linestyle='-', color='red', label='Árvore B+')

# Linha do Hash (Azul)
plt.plot(registros, tempo_hash, marker='s', linestyle='--', color='blue', label='Hash Extensível')

plt.title('Comparativo de Performance: Inserção')
plt.xlabel('Quantidade de Registros')
plt.ylabel('Tempo (segundos)')
plt.grid(True)
plt.legend()
plt.xticks(registros) # Força mostrar apenas os valores testados no eixo X

# Salva a imagem
plt.savefig('grafico_resultados.png')
print("Gráfico salvo como 'grafico_resultados.png'")
plt.show()