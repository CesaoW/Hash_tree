# -*- coding: utf-8 -*-

"""
Script de experimentos automatizados para B-Tree e Linear Hashing
Gera datasets e executa testes com diferentes configurações
"""

import subprocess
import time
import csv
import os
import argparse
from datetime import datetime


class ExperimentRunner:
    '''Classe para executar e gerenciar experimentos'''
    
    def __init__(self, output_dir='results'):
        self.output_dir = output_dir
        self.results = []
        
        # Criar diretório de resultados
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Arquivo de resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.results_file = os.path.join(output_dir, f'results_{timestamp}.csv')
    
    def generate_dataset(self, attributes, insertions, deletions, filename):
        '''Gera dataset usando SIOgen'''
        print(f"\n📊 Generating dataset: {filename}")
        print(f"   Attributes: {attributes}, Insertions: {insertions}, Deletions: {deletions}")
        
        # Comando SIOgen
        cmd = [
            './siogen',
            '-a', str(attributes),
            '-i', str(insertions),
            '-d', str(deletions),
            '-f', filename
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"   ✓ Dataset generated successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ✗ Error generating dataset: {e}")
            return False
        except FileNotFoundError:
            print(f"   ✗ SIOgen not found. Please install it first.")
            print(f"      See: https://ribeiromarcos.github.io/siogen/")
            return False
    
    def run_index(self, index_type, filename, page_size, **kwargs):
        '''Executa índice e coleta estatísticas'''
        print(f"\n🔧 Running {index_type.upper()} index")
        print(f"   File: {filename}, Page size: {page_size}")
        
        # Monta comando
        cmd = [
            'python', 'main.py',
            '-t', index_type,
            '-f', filename,
            '-p', str(page_size),
            '-s'
        ]
        
        # Adiciona parâmetros específicos do Linear Hash
        if index_type == 'linear':
            if 'buckets' in kwargs:
                cmd.extend(['-b', str(kwargs['buckets'])])
            if 'utilization' in kwargs:
                cmd.extend(['-u', str(kwargs['utilization'])])
        
        # Adiciona busca por intervalo (B-Tree)
        if index_type == 'btree' and 'range_search' in kwargs:
            min_key, max_key = kwargs['range_search']
            cmd.extend(['--range', str(min_key), str(max_key)])
        
        # Executa
        start_time = time.time()
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            elapsed_time = time.time() - start_time
            
            print(f"   ✓ Execution completed in {elapsed_time:.2f}s")
            
            # Parse output para extrair estatísticas
            stats = self._parse_output(result.stdout)
            stats['execution_time'] = elapsed_time
            stats['index_type'] = index_type
            stats['filename'] = filename
            stats['page_size'] = page_size
            
            if index_type == 'linear':
                stats['buckets'] = kwargs.get('buckets', 4)
                stats['utilization'] = kwargs.get('utilization', 0.8)
            
            return stats
            
        except subprocess.CalledProcessError as e:
            print(f"   ✗ Error executing index: {e}")
            return None
    
    def _parse_output(self, output):
        '''Parse output para extrair estatísticas'''
        stats = {}
        
        # Parseia linhas de estatísticas
        for line in output.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('='):
                key, value = line.split(':', 1)
                key = key.strip().replace(' ', '_').lower()
                value = value.strip()
                
                # Tenta converter para número
                try:
                    if '.' in value:
                        stats[key] = float(value.split()[0])
                    else:
                        stats[key] = int(value.split()[0])
                except:
                    stats[key] = value
        
        return stats
    
    def save_results(self):
        '''Salva resultados em CSV'''
        if not self.results:
            print("\n⚠️  No results to save")
            return
        
        print(f"\n💾 Saving results to {self.results_file}")
        
        # Coleta todas as chaves possíveis
        all_keys = set()
        for result in self.results:
            all_keys.update(result.keys())
        
        # Escreve CSV
        with open(self.results_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"   ✓ Results saved successfully")
    
    def run_experiment(self, exp_config):
        '''Executa um experimento completo'''
        print("\n" + "="*70)
        print(f"EXPERIMENT: {exp_config['name']}")
        print("="*70)
        
        # Gera dataset
        dataset_file = os.path.join('data', exp_config['dataset_file'])
        
        if not os.path.exists(dataset_file):
            success = self.generate_dataset(
                exp_config['attributes'],
                exp_config['insertions'],
                exp_config['deletions'],
                dataset_file
            )
            if not success:
                return
        else:
            print(f"\n📊 Using existing dataset: {dataset_file}")
        
        # Executa índices
        for index_type in exp_config.get('index_types', ['btree', 'linear']):
            for page_size in exp_config.get('page_sizes', [512]):
                
                # Parâmetros específicos
                kwargs = {}
                
                if index_type == 'linear':
                    for buckets in exp_config.get('buckets', [4]):
                        for util in exp_config.get('utilization', [0.8]):
                            kwargs = {'buckets': buckets, 'utilization': util}
                            stats = self.run_index(index_type, dataset_file, page_size, **kwargs)
                            
                            if stats:
                                stats['experiment'] = exp_config['name']
                                self.results.append(stats)
                else:
                    # B-Tree
                    stats = self.run_index(index_type, dataset_file, page_size, **kwargs)
                    
                    if stats:
                        stats['experiment'] = exp_config['name']
                        self.results.append(stats)


def default_experiments():
    '''Define experimentos padrão'''
    experiments = [
        {
            'name': 'Exp1_PageSize_Variation',
            'dataset_file': 'exp1_data.csv',
            'attributes': 3,
            'insertions': 10000,
            'deletions': 1000,
            'index_types': ['btree', 'linear'],
            'page_sizes': [256, 512, 1024, 2048],
            'buckets': [4],
            'utilization': [0.8]
        },
        {
            'name': 'Exp2_Attributes_Variation',
            'dataset_file': 'exp2_attrs_{}.csv',
            'base_config': {
                'insertions': 10000,
                'deletions': 1000,
                'index_types': ['btree', 'linear'],
                'page_sizes': [512],
                'buckets': [4],
                'utilization': [0.8]
            },
            'variations': [
                {'attributes': 3},
                {'attributes': 5},
                {'attributes': 10},
                {'attributes': 15}
            ]
        },
        {
            'name': 'Exp3_Scale_Test',
            'dataset_file': 'exp3_scale_{}.csv',
            'base_config': {
                'attributes': 5,
                'index_types': ['btree', 'linear'],
                'page_sizes': [512],
                'buckets': [4],
                'utilization': [0.8]
            },
            'variations': [
                {'insertions': 1000, 'deletions': 100},
                {'insertions': 5000, 'deletions': 500},
                {'insertions': 10000, 'deletions': 1000},
                {'insertions': 50000, 'deletions': 5000},
                {'insertions': 100000, 'deletions': 10000}
            ]
        },
        {
            'name': 'Exp4_Linear_Hash_Buckets',
            'dataset_file': 'exp4_data.csv',
            'attributes': 5,
            'insertions': 20000,
            'deletions': 2000,
            'index_types': ['linear'],
            'page_sizes': [512],
            'buckets': [2, 4, 8, 16, 32],
            'utilization': [0.8]
        },
        {
            'name': 'Exp5_Linear_Hash_Utilization',
            'dataset_file': 'exp5_data.csv',
            'attributes': 5,
            'insertions': 20000,
            'deletions': 2000,
            'index_types': ['linear'],
            'page_sizes': [512],
            'buckets': [4],
            'utilization': [0.5, 0.6, 0.7, 0.8, 0.9]
        }
    ]
    
    return experiments


def main():
    parser = argparse.ArgumentParser(description='Run automated experiments')
    parser.add_argument('--experiments', nargs='+', type=int,
                       help='Experiment numbers to run (default: all)')
    parser.add_argument('--output-dir', default='results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  AUTOMATED EXPERIMENTS - INDEX STRUCTURES")
    print("="*70)
    print("\nThis script will run automated experiments to evaluate:")
    print("  • B-Tree performance")
    print("  • Linear Hashing performance")
    print("  • Effects of page size")
    print("  • Effects of number of attributes")
    print("  • Scalability")
    print("\nResults will be saved to CSV files for analysis.")
    print("\nNote: This requires SIOgen to be installed and available.")
    print("      See: https://ribeiromarcos.github.io/siogen/")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    # Cria runner
    runner = ExperimentRunner(args.output_dir)
    
    # Carrega experimentos
    experiments = default_experiments()
    
    # Filtra experimentos se especificado
    if args.experiments:
        experiments = [exp for i, exp in enumerate(experiments, 1) 
                      if i in args.experiments]
    
    print(f"\n📋 Running {len(experiments)} experiment(s)...\n")
    
    # Executa experimentos
    for i, exp_config in enumerate(experiments, 1):
        print(f"\n{'='*70}")
        print(f"RUNNING EXPERIMENT {i}/{len(experiments)}")
        print(f"{'='*70}")
        
        # Trata experimentos com variações
        if 'variations' in exp_config:
            base = exp_config['base_config']
            for j, var in enumerate(exp_config['variations'], 1):
                config = {
                    'name': f"{exp_config['name']}_Var{j}",
                    'dataset_file': exp_config['dataset_file'].format(j),
                    **base,
                    **var
                }
                runner.run_experiment(config)
        else:
            runner.run_experiment(exp_config)
    
    # Salva resultados
    runner.save_results()
    
    print("\n" + "="*70)
    print("  ALL EXPERIMENTS COMPLETED")
    print("="*70)
    print(f"\n📊 Total experiments run: {len(runner.results)}")
    print(f"📁 Results saved to: {runner.results_file}")
    print("\n✓ Done!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Experiments interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()