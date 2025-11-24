# -*- coding: utf-8 -*-

"""
Performance Analysis and Plotting for B-Tree and Linear Hash
Analyzes execution times and generates comparison charts
"""

import matplotlib.pyplot as plt
import argparse
import json
import os
from datetime import datetime


def load_results(filename):
    """Load performance results from JSON file"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Results file not found: {filename}")
    
    with open(filename, 'r') as f:
        return json.load(f)


def plot_comparison(results, output='grafico_resultados.png'):
    """Generate comparison plot"""
    
    # Extract data
    registros = results['registros']
    tempo_btree = results['btree']
    tempo_linear_hash = results['linear_hash']
    
    # Se tiver apenas 1 ponto, fazer gráfico de barras
    if len(registros) == 1:
        plot_bar_chart(results, output)
    else:
        plot_line_chart(results, output)


def plot_bar_chart(results, output):
    """Generate bar chart for single data point comparison"""
    
    registros = results['registros'][0]
    tempo_btree = results['btree'][0]
    tempo_linear_hash = results['linear_hash'][0]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # === SUBPLOT 1: Tempo Total ===
    structures = ['Árvore B', 'Linear\nHashing']
    times = [tempo_btree, tempo_linear_hash]
    colors = ['#E74C3C', '#3498DB']
    
    bars1 = ax1.bar(structures, times, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    
    # Add values on bars
    for bar, time in zip(bars1, times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{time:.2f}s',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax1.set_ylabel('Tempo (segundos)', fontsize=12, fontweight='bold')
    ax1.set_title('Tempo Total de Carregamento', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, max(times) * 1.2)
    
    # Add warning
    if 'btree_stats' in results and results['btree_stats']['num_records'] < registros:
        ax1.text(0, max(times) * 1.1, 
                f"⚠️ Árvore B: apenas {results['btree_stats']['num_records']} registros",
                fontsize=9, color='red', ha='center')
    
    # === SUBPLOT 2: Tempo por Registro ===
    btree_records = results.get('btree_stats', {}).get('num_records', registros)
    lhash_records = results.get('linear_hash_stats', {}).get('num_records', registros)
    
    time_per_record_btree = (tempo_btree / btree_records) * 1000  # ms
    time_per_record_lhash = (tempo_linear_hash / lhash_records) * 1000  # ms
    
    times_per_record = [time_per_record_btree, time_per_record_lhash]
    
    bars2 = ax2.bar(structures, times_per_record, color=colors, alpha=0.8, 
                    edgecolor='white', linewidth=2)
    
    # Add values on bars
    for bar, time in zip(bars2, times_per_record):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{time:.2f}ms',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax2.set_ylabel('Tempo (milissegundos)', fontsize=12, fontweight='bold')
    ax2.set_title('Tempo por Registro Inserido', fontsize=14, fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_ylim(0, max(times_per_record) * 1.2)
    
    # Add speedup annotation
    if time_per_record_lhash < time_per_record_btree:
        speedup = time_per_record_btree / time_per_record_lhash
        ax2.text(1, max(times_per_record) * 1.1,
                f'Linear Hash {speedup:.2f}x mais rápido',
                fontsize=10, ha='center', style='italic',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
    
    # Main title
    fig.suptitle(f'Comparativo de Performance - {registros:,} Registros'.replace(',', '.'),
                fontsize=16, fontweight='bold', y=0.98)
    
    # Add footer with details
    footer_text = f"Tamanho da página: {results.get('page_size', 512)} bytes"
    if 'btree_stats' in results:
        footer_text += f" | Árvore B: {results['btree_stats']['num_records']} registros efetivos"
    fig.text(0.5, 0.02, footer_text, ha='center', fontsize=9, style='italic', color='gray')
    
    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico salvo como '{output}'")
    plt.show()


def plot_line_chart(results, output):
    """Generate line chart for multiple data points"""
    
    registros = results['registros']
    tempo_btree = results['btree']
    tempo_linear_hash = results['linear_hash']
    
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot lines
    ax.plot(registros, tempo_btree, 
            marker='o', linestyle='-', linewidth=2.5, markersize=10,
            color='#E74C3C', label='Árvore B',
            markeredgewidth=2, markeredgecolor='white')
    
    ax.plot(registros, tempo_linear_hash, 
            marker='s', linestyle='--', linewidth=2.5, markersize=10,
            color='#3498DB', label='Linear Hashing',
            markeredgewidth=2, markeredgecolor='white')
    
    # Annotate values
    for i, (x, y) in enumerate(zip(registros, tempo_btree)):
        ax.annotate(f'{y:.4f}s', xy=(x, y), xytext=(0, 10),
                    textcoords='offset points', ha='center', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#E74C3C', 
                             alpha=0.7, edgecolor='none'),
                    color='white', fontweight='bold')
    
    for i, (x, y) in enumerate(zip(registros, tempo_linear_hash)):
        ax.annotate(f'{y:.4f}s', xy=(x, y), xytext=(0, -15),
                    textcoords='offset points', ha='center', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#3498DB', 
                             alpha=0.7, edgecolor='none'),
                    color='white', fontweight='bold')
    
    ax.set_title('Comparativo de Performance: Tempo de Carregamento', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Quantidade de Registros', fontsize=13, fontweight='bold')
    ax.set_ylabel('Tempo (segundos)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_xticks(registros)
    ax.set_xticklabels([f'{r:,}'.replace(',', '.') for r in registros])
    ax.legend(fontsize=12, loc='upper left', framealpha=0.9, edgecolor='gray')
    
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico salvo como '{output}'")
    plt.show()


def print_statistics(results):
    """Print detailed statistics"""
    registros = results['registros']
    tempo_btree = results['btree']
    tempo_linear_hash = results['linear_hash']
    
    print("\n" + "="*70)
    print("ANÁLISE DE PERFORMANCE")
    print("="*70)
    
    for i, n_reg in enumerate(registros):
        print(f"\n{n_reg:,} registros (esperados):".replace(',', '.'))
        print(f"  Árvore B:")
        print(f"    Tempo total:     {tempo_btree[i]:.4f}s")
        
        if 'btree_stats' in results:
            actual_records = results['btree_stats']['num_records']
            print(f"    Registros reais: {actual_records} ({actual_records/n_reg*100:.1f}%)")
            print(f"    Tempo/registro:  {tempo_btree[i]/actual_records*1000:.2f} ms")
        
        print(f"  Linear Hashing:")
        print(f"    Tempo total:     {tempo_linear_hash[i]:.4f}s")
        
        if 'linear_hash_stats' in results:
            actual_records = results['linear_hash_stats']['num_records']
            print(f"    Registros reais: {actual_records} ({actual_records/n_reg*100:.1f}%)")
            print(f"    Tempo/registro:  {tempo_linear_hash[i]/actual_records*1000:.2f} ms")
        
        # Speedup bruto (enganoso se há problema de integridade)
        if tempo_btree[i] > tempo_linear_hash[i]:
            speedup = tempo_btree[i] / tempo_linear_hash[i]
            print(f"\n  ⚠️  Aparente: Linear Hash é {speedup:.2f}x mais rápido")
            print(f"      (mas Árvore B processou menos dados!)")
        else:
            speedup = tempo_linear_hash[i] / tempo_btree[i]
            print(f"\n  Speedup: Árvore B é {speedup:.2f}x mais rápida")
    
    # Análise de estrutura
    if 'btree_stats' in results and 'linear_hash_stats' in results:
        print("\n" + "="*70)
        print("ANÁLISE DE ESTRUTURA")
        print("="*70)
        
        btree = results['btree_stats']
        lhash = results['linear_hash_stats']
        
        print("\nÁrvore B:")
        print(f"  Altura:           {btree.get('height', 'N/A')}")
        print(f"  Total de nós:     {btree.get('num_nodes', 'N/A')}")
        print(f"  Nós folha:        {btree.get('num_leaf_nodes', 'N/A')}")
        print(f"  Registros:        {btree.get('num_records', 'N/A')}")
        
        print("\nLinear Hashing:")
        print(f"  Nível:            {lhash.get('level', 'N/A')}")
        print(f"  Buckets:          {lhash.get('num_buckets', 'N/A')}")
        print(f"  Registros:        {lhash.get('num_records', 'N/A')}")
        print(f"  Páginas overflow: {lhash.get('overflow_pages', 'N/A')}")
        print(f"  Buckets c/ ovfl:  {lhash.get('buckets_with_overflow', 'N/A')}")
        print(f"  Média reg/bucket: {lhash.get('avg_records_per_bucket', 'N/A'):.2f}")
        print(f"  Total splits:     {lhash.get('num_splits', 'N/A')}")
        
        # Uso de espaço
        page_size = results.get('page_size', 512)
        btree_pages = btree.get('num_nodes', 0)
        lhash_pages = lhash.get('num_buckets', 0) + lhash.get('overflow_pages', 0)
        
        btree_kb = (btree_pages * page_size) / 1024
        lhash_kb = (lhash_pages * page_size) / 1024
        
        print(f"\nUso de Espaço (página = {page_size} bytes):")
        print(f"  Árvore B:       {btree_pages:4d} páginas = {btree_kb:7.2f} KB")
        print(f"  Linear Hash:    {lhash_pages:4d} páginas = {lhash_kb:7.2f} KB")
        
        if lhash_kb > btree_kb:
            overhead = (lhash_kb / btree_kb - 1) * 100
            print(f"  → Linear Hash usa {overhead:.1f}% mais espaço")
        else:
            overhead = (btree_kb / lhash_kb - 1) * 100
            print(f"  → Árvore B usa {overhead:.1f}% mais espaço")
    
    # Análise adicional
    if 'analysis' in results:
        print("\n" + "="*70)
        print("ANÁLISE NORMALIZADA")
        print("="*70)
        
        analysis = results['analysis']
        
        if 'btree_records_missing' in analysis:
            print(f"\n⚠️  Registros faltando na Árvore B: {analysis['btree_records_missing']}")
        
        if 'btree_ms_per_record' in analysis and 'linear_hash_ms_per_record' in analysis:
            print(f"\nTempo por registro efetivamente inserido:")
            print(f"  Árvore B:       {analysis['btree_ms_per_record']:.2f} ms/registro")
            print(f"  Linear Hash:    {analysis['linear_hash_ms_per_record']:.2f} ms/registro")
            
            if 'linear_hash_speedup_per_record' in analysis:
                speedup = analysis['linear_hash_speedup_per_record']
                print(f"  → Linear Hash é {speedup:.2f}x mais rápido (por registro real)")
    
    print("\n" + "="*70)


def create_sample_results():
    """Create sample results file"""
    results = {
        'registros': [1000, 10000, 50000],
        'btree': [0.0120, 0.0144, 0.0259],
        'linear_hash': [0.0011, 0.0035, 0.0199],
        'date': datetime.now().isoformat(),
        'page_size': 512
    }
    
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✓ Arquivo de exemplo 'results.json' criado")
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Performance Analysis for B-Tree and Linear Hash',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Criar arquivo de resultados de exemplo
  python plot_performance.py --create-sample
  
  # Plotar resultados de um arquivo JSON
  python plot_performance.py -f results.json
  
  # Plotar e salvar com nome customizado
  python plot_performance.py -f results.json -o meu_grafico.png
  
  # Apenas mostrar estatísticas (sem gráfico)
  python plot_performance.py -f results.json --stats-only

Formato do arquivo JSON:
  {
    "registros": [1000, 10000, 50000],
    "btree": [0.0120, 0.0144, 0.0259],
    "linear_hash": [0.0011, 0.0035, 0.0199]
  }
        ''')
    
    parser.add_argument('-f', '--file', 
                        default='results.json',
                        help='Input JSON file with results (default: results.json)')
    parser.add_argument('-o', '--output', 
                        default='grafico_resultados.png',
                        help='Output image file (default: grafico_resultados.png)')
    parser.add_argument('--stats-only', 
                        action='store_true',
                        help='Show only statistics (no plot)')
    parser.add_argument('--create-sample', 
                        action='store_true',
                        help='Create sample results.json file')
    
    args = parser.parse_args()
    
    try:
        if args.create_sample:
            results = create_sample_results()
            print("\nAgora edite o arquivo 'results.json' com seus dados reais")
            print("e execute: python plot_performance.py -f results.json")
            return 0
        
        # Load results
        results = load_results(args.file)
        
        # Print statistics
        print_statistics(results)
        
        # Generate plot (unless stats-only)
        if not args.stats_only:
            plot_comparison(results, args.output)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n✗ Erro: {e}")
        print("\nDica: Use --create-sample para criar um arquivo de exemplo")
        return 1
    except KeyError as e:
        print(f"\n✗ Erro: Campo obrigatório ausente no JSON: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())