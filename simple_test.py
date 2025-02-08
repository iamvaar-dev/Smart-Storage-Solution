#!/usr/bin/env python3
import os
import subprocess
import hashlib
import shutil

def create_test_file(filename: str, pattern: bytes, repetitions: int):
    """Create a test file with repeating pattern.
    
    Args:
        filename: Output file name
        pattern: Bytes pattern to repeat
        repetitions: Number of times to repeat the pattern
    """
    with open(filename, 'wb') as f:
        for _ in range(repetitions):
            f.write(pattern)

def verify_files(original: str, reconstructed: str) -> bool:
    """Compare two files to ensure they are identical."""
    with open(original, 'rb') as f1, open(reconstructed, 'rb') as f2:
        return hashlib.sha256(f1.read()).digest() == hashlib.sha256(f2.read()).digest()

def create_test6():
    """Create test6.bin with 10-byte pattern repeated 100,000 times."""
    pattern = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A])  # 10 bytes
    repetitions = 100000
    
    with open('test6.bin', 'wb') as f:
        for _ in range(repetitions):
            f.write(pattern)

def analyze_smart_file(smart_file_path):
    """Analyze the .smart file to separate unique data and metadata."""
    with open(smart_file_path, 'rb') as f:
        # Read format type
        format_type = int.from_bytes(f.read(1), 'big')
        
        if format_type == 0x01:  # Pattern-based format
            # Read pattern size (8 bytes)
            pattern_size = int.from_bytes(f.read(8), 'big')
            # Read repetitions (8 bytes)
            repetitions = int.from_bytes(f.read(8), 'big')
            # Read pattern
            pattern = f.read(pattern_size)
            
            return {
                'header_size': 17,  # 1 + 8 + 8 bytes
                'sequence_data': 0,  # No sequence data in pattern mode
                'unique_data': len(pattern),
                'total_size': os.path.getsize(smart_file_path),
                'is_pattern': True,
                'repetitions': repetitions
            }
        else:  # Block-based format
            # Read block size (8 bytes)
            block_size = int.from_bytes(f.read(8), 'big')
            # Read number of blocks (4 bytes)
            num_blocks = int.from_bytes(f.read(4), 'big')
            
            # Calculate sizes
            header_size = 13  # 1 + 8 + 4 bytes
            unique_data_size = num_blocks * block_size
            sequence_size = os.path.getsize(smart_file_path) - header_size - unique_data_size
            
            return {
                'header_size': header_size,
                'sequence_data': sequence_size,
                'unique_data': unique_data_size,
                'total_size': os.path.getsize(smart_file_path),
                'is_pattern': False
            }

def create_test_pattern():
    """Create test file with 0F AB BB pattern repeated 11 times."""
    pattern = bytes([0x0F, 0xAB, 0xBB])  # 3-byte pattern
    repetitions = 11  # Total size will be 33 bytes
    
    with open('pattern_test.bin', 'wb') as f:
    
        for _ in range(repetitions):
            f.write(pattern)

def create_simple_test():
    """Create test file with byte 0x42 repeated 5 times."""
    pattern = bytes([0x42])  # Single byte pattern
    repetitions = 5  # Total size will be 5 bytes
    
    with open('simple_test.bin', 'wb') as f:
        for _ in range(repetitions):
            f.write(pattern)

def analyze_file_pattern(filename: str) -> dict:
    """Analyze file to find the repeating pattern and optimal block size."""
    with open(filename, 'rb') as f:
        data = f.read()
    
    if len(data) < 2:
        return {'pattern': data, 'repetitions': 1, 'block_size': len(data)}
    
    # Try different pattern sizes up to half the file size
    max_pattern_size = len(data) // 2
    for pattern_size in range(1, max_pattern_size + 1):
        pattern = data[:pattern_size]
        if len(data) % pattern_size == 0:
            is_repeating = True
            for i in range(0, len(data), pattern_size):
                if data[i:i + pattern_size] != pattern:
                    is_repeating = False
                    break
            if is_repeating:
                return {
                    'pattern': pattern,
                    'repetitions': len(data) // pattern_size,
                    'block_size': pattern_size
                }
    
    # If no pattern found, return original data
    return {'pattern': data, 'repetitions': 1, 'block_size': len(data)}

def test_compression(input_file: str) -> dict:
    """Test compression and return results."""
    pattern_info = analyze_file_pattern(input_file)
    block_size = pattern_info['block_size']
    
    original_size = os.path.getsize(input_file)
    
    # Compress
    result = subprocess.run(
        ['python', 'deconstruct.py', input_file, str(block_size)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Compression failed: {result.stderr}")
        return None

    smart_file = f"{input_file}.smart"
    smart_size = os.path.getsize(smart_file)
    
    # Reconstruct and verify
    reconstructed = f"{input_file}.reconstructed"
    result = subprocess.run(
        ['python', 'reconstruct.py', smart_file, reconstructed],
        capture_output=True, text=True
    )
    
    success = False
    if result.returncode == 0:
        success = verify_files(input_file, reconstructed)
        if success:
            print("✓ Compression and reconstruction successful")
        else:
            print("✗ Files differ after reconstruction")
    
    return {
        'original_size': original_size,
        'smart_size': smart_size,
        'success': success
    }

def create_test_files():
    """Create 5 different test files with various patterns."""
    # Create reference directory if it doesn't exist
    reference_dir = "reference_files"
    os.makedirs(reference_dir, exist_ok=True)
    
    # Store results for summary
    results = []
    
    test_cases = [
        ("test_16b.bin", bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                               0xFF, 0xFE, 0xFD, 0xFC, 0xFB, 0xFA, 0xF9, 0xF8]), 
         1000, "16-byte pattern"),
        ("test_32b.bin", bytes(range(32)), 
         500, "32-byte sequential"),
        ("test_4b.bin", bytes([0xDE, 0xAD, 0xBE, 0xEF]), 
         10000, "4-byte DEADBEEF"),
        ("test_8b.bin", bytes([0x20, 0x23, 0x10, 0x15, 0x14, 0x30, 0x00, 0x00]), 
         5000, "8-byte timestamp"),
        ("test_64b.bin", bytes([x % 256 for x in range(64)]) * 2, 
         200, "64-byte sequence")
    ]
    
    for filename, pattern, reps, description in test_cases:
        print(f"\nTesting {description}")
        print(f"Pattern size: {len(pattern)} bytes")
        print(f"Repetitions: {reps:,}")
        total_size = len(pattern) * reps
        print(f"Total size: {total_size:,} bytes")
        
        # Create test file
        with open(filename, 'wb') as f:
            for _ in range(reps):
                f.write(pattern)
        
        # Test compression
        result = test_compression(filename)
        
        # Store results
        results.append({
            'description': description,
            'pattern_size': len(pattern),
            'repetitions': reps,
            'original_size': total_size,
            'smart_size': result['smart_size'] if result else 0,
            'success': result['success'] if result else False,
            'filename': filename
        })
        
        # Save reference files
        if result and result['success']:
            # Save original and smart files to reference directory
            for ext in ['', '.smart']:
                src = filename + ext
                dst = os.path.join(reference_dir, os.path.basename(src))
                shutil.copy2(src, dst)
            print(f"✓ Saved reference files to {reference_dir}/")
        
        # Clean up working files only
        try:
            os.remove(filename)  # Remove original from working dir
            os.remove(filename + '.reconstructed')  # Remove reconstructed file
        except FileNotFoundError:
            pass
    
    # Print summary table
    print("\n" + "="*90)
    print("SUMMARY OF ALL TESTS")
    print("="*90)
    print(f"{'Pattern Type':<20} {'Pattern':<8} {'Reps':<8} {'Original':<12} {'Smart':<12} {'Ratio':<8} {'Status'} {'Reference'}")
    print("-"*90)
    
    for r in results:
        status = "✓" if r['success'] else "✗"
        ratio = (r['smart_size'] / r['original_size'] * 100) if r['original_size'] > 0 else 0
        ref_file = os.path.join(reference_dir, os.path.basename(r['filename']) + '.smart')
        ref_status = "Saved" if os.path.exists(ref_file) else "Failed"
        
        print(f"{r['description']:<20} "
              f"{r['pattern_size']:<8} "
              f"{r['repetitions']:<8,} "
              f"{r['original_size']:<12,} "
              f"{r['smart_size']:<12,} "
              f"{ratio:<8.2f}% "
              f"{status}     "
              f"{ref_status}")
    print("="*90)
    print(f"\nReference files are saved in: {os.path.abspath(reference_dir)}/")

def create_test_suite():
    """Create and test 100 different pattern files with varying characteristics."""
    results = []
    
    test_cases = [
        # 1. Simple repeating bytes (10 tests)
        *[(f"simple_{i}.bin", bytes([i]), 1000, f"Single byte 0x{i:02X}")
          for i in range(10)],
        
        # 2. Small patterns (2-4 bytes) (20 tests)
        *[(f"small_{i}.bin", bytes([i, i+1, i+2]), 500, f"3-byte increment {i}")
          for i in range(10)],
        *[(f"small_alt_{i}.bin", bytes([0xFF, i, 0x00, i]), 500, f"4-byte alternating {i}")
          for i in range(10)],
        
        # 3. Medium patterns (8-16 bytes) (20 tests)
        *[(f"med_{i}.bin", bytes(range(i, i+8)), 200, f"8-byte sequence {i}")
          for i in range(10)],
        *[(f"med_rev_{i}.bin", bytes(range(15-i, 15-i+16)), 200, f"16-byte reverse {i}")
          for i in range(10)],
        
        # 4. Large patterns (32-64 bytes) (20 tests)
        *[(f"large_{i}.bin", bytes([x % (i+1) for x in range(32)]), 100, f"32-byte mod{i+1}")
          for i in range(10)],
        *[(f"large_comp_{i}.bin", bytes([i ^ x for x in range(64)]), 50, f"64-byte XOR {i}")
          for i in range(10)],
        
        # 5. Complex patterns (30 tests)
        *[(f"complex_{i}.bin", 
           bytes([x if x % 2 == 0 else 255-x for x in range(16)]) * (i+1),
           100, f"Complex alternating {i}")
          for i in range(10)],
        *[(f"complex_rep_{i}.bin",
           bytes([i, i*2, i*3, 0xFF, 0xAA]) * (i+2),
           200, f"Complex repeating {i}")
          for i in range(10)],
        *[(f"complex_mix_{i}.bin",
           bytes([x ^ (i*8) for x in range(24)]) + bytes([0xAA, 0xBB, 0xCC] * i),
           150, f"Complex mixed {i}")
          for i in range(10)]
    ]
    
    pattern_stats = {
        'ratios': [],
        'sizes': [],
        'success_rate': 0,
        'best_ratio': float('inf'),
        'worst_ratio': 100.0,  # Changed from 0 to 100
        'best_pattern': None,
        'worst_pattern': None,
        'failed_compressions': []  # Track failed compressions
    }
    
    print("\nRunning 100 Pattern Tests...")
    print("-" * 80)
    print(f"{'Pattern Type':<25} {'Original':<10} {'Smart':<10} {'Ratio':<8} {'Status'}")
    print("-" * 80)
    
    for filename, pattern, reps, description in test_cases:
        total_size = len(pattern) * reps
        
        # Create test file
        with open(filename, 'wb') as f:
            for _ in range(reps):
                f.write(pattern)
        
        result = test_compression(filename)
        
        if result:
            ratio = (result['smart_size'] / result['original_size']) * 100
            # Only consider it successful if compression actually reduced size
            is_successful = result['success'] and result['smart_size'] < result['original_size']
            
            if is_successful:
                pattern_stats['ratios'].append(ratio)
                pattern_stats['sizes'].append(result['smart_size'])
                
                # Track best compression (lowest ratio)
                if ratio < pattern_stats['best_ratio']:
                    pattern_stats['best_ratio'] = ratio
                    pattern_stats['best_pattern'] = {
                        'description': description,
                        'size': len(pattern),
                        'ratio': ratio,
                        'original_size': total_size,
                        'smart_size': result['smart_size']
                    }
                
                # Track worst successful compression (highest ratio < 100%)
                if ratio < 100 and ratio > pattern_stats['worst_ratio']:
                    pattern_stats['worst_ratio'] = ratio
                    pattern_stats['worst_pattern'] = {
                        'description': description,
                        'size': len(pattern),
                        'ratio': ratio,
                        'original_size': total_size,
                        'smart_size': result['smart_size']
                    }
            else:
                pattern_stats['failed_compressions'].append({
                    'description': description,
                    'size': len(pattern),
                    'ratio': ratio,
                    'original_size': total_size,
                    'smart_size': result['smart_size']
                })
            
            status = "✓" if is_successful else "✗"
            print(f"{description:<25} {total_size:<10,d} {result['smart_size']:<10,d} {ratio:<8.2f}% {status}")
        
        # Cleanup
        try:
            os.remove(filename)
            os.remove(filename + '.smart')
            os.remove(filename + '.reconstructed')
        except FileNotFoundError:
            pass
    
    # Calculate statistics
    total_tests = len(test_cases)
    successful_tests = len(pattern_stats['ratios'])
    pattern_stats['success_rate'] = (successful_tests / total_tests) * 100
    
    print("\n=== Compression Analysis Report ===")
    print("\nOverall Statistics:")
    print(f"Total tests: {total_tests}")
    print(f"Successful compressions: {successful_tests}")
    print(f"Success rate: {pattern_stats['success_rate']:.2f}%")
    
    if successful_tests > 0:
        print(f"Average compression ratio: {sum(pattern_stats['ratios'])/len(pattern_stats['ratios']):.2f}%")
        print(f"Median compression ratio: {sorted(pattern_stats['ratios'])[len(pattern_stats['ratios'])//2]:.2f}%")
        
        print("\nBest Compression:")
        print(f"Pattern: {pattern_stats['best_pattern']['description']}")
        print(f"Original size: {pattern_stats['best_pattern']['original_size']:,} bytes")
        print(f"Compressed size: {pattern_stats['best_pattern']['smart_size']:,} bytes")
        print(f"Ratio: {pattern_stats['best_pattern']['ratio']:.2f}%")
        
        if pattern_stats['worst_pattern']:
            print("\nWorst Successful Compression:")
            print(f"Pattern: {pattern_stats['worst_pattern']['description']}")
            print(f"Original size: {pattern_stats['worst_pattern']['original_size']:,} bytes")
            print(f"Compressed size: {pattern_stats['worst_pattern']['smart_size']:,} bytes")
            print(f"Ratio: {pattern_stats['worst_pattern']['ratio']:.2f}%")
    
    print("\nCompression Ratio Distribution (successful only):")
    ranges = [(0,25), (25,50), (50,75), (75,100)]
    for start, end in ranges:
        count = len([r for r in pattern_stats['ratios'] if start <= r < end])
        print(f"{start:>3}-{end:<3}%: {count:>3} tests {'#' * (count * 50 // len(test_cases))}")
    
    if pattern_stats['failed_compressions']:
        print("\nFailed Compressions (ratio ≥ 100%):")
        for fail in pattern_stats['failed_compressions'][:5]:  # Show first 5 failures
            print(f"- {fail['description']}: {fail['ratio']:.2f}% " +
                  f"({fail['original_size']:,} → {fail['smart_size']:,} bytes)")
        if len(pattern_stats['failed_compressions']) > 5:
            print(f"  ... and {len(pattern_stats['failed_compressions'])-5} more")

def main():
    print("=== Comprehensive Pattern Compression Test Suite ===")
    create_test_suite()

if __name__ == "__main__":
    main() 