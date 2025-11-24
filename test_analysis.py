# -*- coding: utf-8 -*-

"""
Test script to compare B-Tree and Linear Hash insertion
"""

import time
import csv
from btree import BTreeIndex
from linear_hash import LinearHashIndex


def count_csv_operations(filename):
    """Count operations in CSV file"""
    counts = {'+': 0, '-': 0, '?': 0, 'empty': 0}
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for line in reader:
            if not line or len(line) == 0:
                counts['empty'] += 1
            elif len(line) >= 1:
                op = line[0]
                if op in counts:
                    counts[op] += 1
    
    return counts


def test_structure(structure_type, filename, page_size=512):
    """Test a structure and return statistics"""
    
    print(f"\n{'='*70}")
    print(f"  TESTING {structure_type.upper()}")
    print(f"{'='*70}\n")
    
    # Create index
    if structure_type == 'btree':
        index = BTreeIndex(page_size, f'{structure_type}_test.log', debugging=False)
    else:
        index = LinearHashIndex(page_size, f'{structure_type}_test.log', 
                               initial_buckets=4, utilization=0.8, debugging=False)
    
    # Load file and measure time
    start_time = time.time()
    index.load_file(filename)
    load_time = time.time() - start_time
    
    # Get statistics
    stats = index.get_statistics()
    stats['load_time'] = load_time
    
    # Print results
    print(f"Statistics for {structure_type}:")
    for key, value in stats.items():
        if key == 'load_time':
            print(f"  {key}: {value:.4f} seconds")
        elif isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    return stats


def main():
    filename = 'data/output.csv'
    
    print("="*70)
    print("  COMPARATIVE TEST: B-TREE vs LINEAR HASH")
    print("="*70)
    
    # Count operations in file
    print("\nAnalyzing CSV file...")
    counts = count_csv_operations(filename)
    print(f"\nOperations in file:")
    print(f"  Insertions (+): {counts['+']}")
    print(f"  Deletions (-):  {counts['-']}")
    print(f"  Searches (?):   {counts['?']}")
    print(f"  Empty lines:    {counts['empty']}")
    print(f"  Expected final records: {counts['+'] - counts['-']}")
    
    # Test B-Tree
    btree_stats = test_structure('btree', filename)
    
    # Test Linear Hash
    lhash_stats = test_structure('linear_hash', filename)
    
    # Comparison
    print(f"\n{'='*70}")
    print("  COMPARISON")
    print(f"{'='*70}\n")
    
    print(f"Records processed:")
    print(f"  B-Tree:       {btree_stats.get('num_records', 'N/A')}")
    print(f"  Linear Hash:  {lhash_stats.get('num_records', 'N/A')}")
    
    btree_time = btree_stats['load_time']
    lhash_time = lhash_stats['load_time']
    
    print(f"\nLoad time:")
    print(f"  B-Tree:       {btree_time:.4f}s")
    print(f"  Linear Hash:  {lhash_time:.4f}s")
    
    if btree_time > lhash_time:
        speedup = btree_time / lhash_time
        print(f"  → Linear Hash is {speedup:.2f}x faster")
    else:
        speedup = lhash_time / btree_time
        print(f"  → B-Tree is {speedup:.2f}x faster")
    
    # Check for problems
    expected_records = counts['+'] - counts['-']
    btree_records = btree_stats.get('num_records', 0)
    lhash_records = lhash_stats.get('num_records', 0)
    
    print(f"\n{'='*70}")
    print("  DATA INTEGRITY CHECK")
    print(f"{'='*70}\n")
    
    if btree_records != expected_records:
        print(f"⚠️  WARNING: B-Tree has {btree_records} records, expected {expected_records}")
        print(f"   Missing: {expected_records - btree_records} records")
    else:
        print(f"✓  B-Tree: OK ({btree_records} records)")
    
    if lhash_records != expected_records:
        print(f"⚠️  WARNING: Linear Hash has {lhash_records} records, expected {expected_records}")
        print(f"   Difference: {abs(lhash_records - expected_records)} records")
    else:
        print(f"✓  Linear Hash: OK ({lhash_records} records)")
    
    print("\n" + "="*70)
    
    # Create results JSON
    import json
    results = {
        "csv_file": filename,
        "page_size": 512,
        "expected_records": expected_records,
        "btree": {
            "load_time": btree_time,
            "stats": btree_stats
        },
        "linear_hash": {
            "load_time": lhash_time,
            "stats": lhash_stats
        }
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Detailed results saved to 'test_results.json'")


if __name__ == '__main__':
    main()