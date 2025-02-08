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
    """Create and test 100 different pattern files with specific byte patterns."""
    test_cases = [
        # 1. Simple repeating patterns (20 tests)
        ("repeat_0F.bin", bytes([0x0F]) * 100, "Single 0F byte * 100"),
        ("repeat_DEAD.bin", bytes([0xDE, 0xAD]) * 50, "DEAD * 50"),
        ("repeat_BEEF.bin", bytes([0xBE, 0xEF]) * 50, "BEEF * 50"),
        ("repeat_CAFE.bin", bytes([0xCA, 0xFE]) * 50, "CAFE * 50"),
        ("repeat_0FAB.bin", bytes([0x0F, 0xAB]) * 50, "0FAB * 50"),
        ("pattern_3byte.bin", bytes([0x0F, 0xAB, 0xBB]) * 11, "0FABBB * 11"),
        ("pattern_4byte.bin", bytes([0xDE, 0xAD, 0xBE, 0xEF]) * 25, "DEADBEEF * 25"),
        ("pattern_5byte.bin", bytes([0xCA, 0xFE, 0xBA, 0xBE, 0x00]) * 20, "CAFEBABE00 * 20"),
        ("pattern_deadcode.bin", bytes([0xDE, 0xAD, 0xC0, 0xDE]) * 25, "DEADC0DE * 25"),
        ("pattern_mixed.bin", bytes([0xFF, 0x00, 0xAA, 0x55]) * 25, "FF00AA55 * 25")
    ]
    
    pattern_stats = {
        'ratios': [],
        'sizes': [],
        'success_rate': 0,
        'best_ratio': float('inf'),
        'worst_ratio': 100.0,
        'best_pattern': None,
        'worst_pattern': None,
        'failed_compressions': []
    }
    
    total_stats = {
        'total_original_size': 0,
        'total_smart_size': 0,
        'total_saved_bytes': 0,
        'pattern_sizes': [],
    }
    
    print("\nRunning Pattern Tests...")
    print("-" * 100)
    print(f"{'Pattern Type':<30} {'Pattern':<20} {'Original':<10} {'Smart':<10} {'Ratio':<8} {'Status'}")
    print("-" * 100)
    
    for filename, content, description in test_cases:
        # First create the test file
        create_test_file(filename, content, 1)  # repetitions=1 since content already has repetitions
        
        original_size = len(content)
        total_stats['total_original_size'] += original_size
        total_stats['pattern_sizes'].append(len(content))
        
        result = test_compression(filename)
        
        if result:
            ratio = (result['smart_size'] / original_size) * 100
            is_successful = result['success'] and result['smart_size'] < original_size
            
            if is_successful:
                pattern_stats['ratios'].append(ratio)
                pattern_stats['sizes'].append(result['smart_size'])
                total_stats['total_smart_size'] += result['smart_size']
                total_stats['total_saved_bytes'] += (original_size - result['smart_size'])
                
                # Analyze smart file format
                smart_analysis = analyze_smart_file(f"{filename}.smart")
                
                if ratio < pattern_stats['best_ratio']:
                    pattern_stats['best_ratio'] = ratio
                    pattern_stats['best_pattern'] = {
                        'description': description,
                        'pattern': content[:16].hex(' '),
                        'ratio': ratio,
                        'original_size': original_size,
                        'smart_size': result['smart_size']
                    }
                
                if ratio < 100 and ratio > pattern_stats['worst_ratio']:
                    pattern_stats['worst_ratio'] = ratio
                    pattern_stats['worst_pattern'] = {
                        'description': description,
                        'pattern': content[:16].hex(' '),
                        'ratio': ratio,
                        'original_size': original_size,
                        'smart_size': result['smart_size']
                    }
            else:
                pattern_stats['failed_compressions'].append({
                    'description': description,
                    'pattern': content[:16].hex(' '),
                    'ratio': ratio,
                    'original_size': original_size,
                    'smart_size': result['smart_size']
                })
            
            status = "✓" if is_successful else "✗"
            pattern_preview = content[:8].hex(' ')
            print(f"{description:<30} {pattern_preview:<20} {original_size:<10} "
                  f"{result['smart_size']:<10} {ratio:<8.2f}% {status}")
        
        # Cleanup
        try:
            os.remove(filename)
            os.remove(f"{filename}.smart")
            os.remove(f"{filename}.reconstructed")
        except FileNotFoundError:
            pass
    
    # Calculate and print statistics
    total_tests = len(test_cases)
    successful_tests = len(pattern_stats['ratios'])
    pattern_stats['success_rate'] = (successful_tests / total_tests) * 100
    
    overall_ratio = (total_stats['total_smart_size'] / total_stats['total_original_size'] * 100) \
        if total_stats['total_original_size'] > 0 else 0
    
    print("\n=== Overall Size Statistics ===")
    print(f"Total original size: {total_stats['total_original_size']:,} bytes")
    print(f"Total compressed size: {total_stats['total_smart_size']:,} bytes")
    print(f"Total bytes saved: {total_stats['total_saved_bytes']:,} bytes")
    print(f"Overall compression ratio: {overall_ratio:.2f}%")
    print(f"Space saving: {100 - overall_ratio:.2f}%")
    
    print("\n=== Pattern Analysis ===")
    if total_stats['pattern_sizes']:
        print(f"Average pattern size: {sum(total_stats['pattern_sizes'])/len(total_stats['pattern_sizes']):.1f} bytes")
        print(f"Smallest pattern: {min(total_stats['pattern_sizes']):,} bytes")
        print(f"Largest pattern: {max(total_stats['pattern_sizes']):,} bytes")

def create_test_case2():
    """Create a test file that matches Case 2 from the assignment.
    
    Creates a file with the same 10 bytes repeated 100,000 times,
    which would normally require 1MB of storage.
    The smart storage should only require 10 bytes (ignoring overhead).
    """
    pattern = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A])  # 10 bytes
    repetitions = 100000  # Will create a 1MB file (10 * 100000 = 1,000,000 bytes)
    filename = "case2_test.bin"
    
    print(f"\nCreating Case 2 test file: {filename}")
    print(f"Pattern size: 10 bytes")
    print(f"Repetitions: {repetitions:,}")
    print(f"Total size: {10 * repetitions:,} bytes (≈ 1MB)")
    
    create_test_file(filename, pattern, repetitions)
    
    # Test compression
    result = test_compression(filename)
    
    if result:
        ratio = (result['smart_size'] / result['original_size']) * 100
        print("\nResults:")
        print(f"Original size: {result['original_size']:,} bytes")
        print(f"Smart size: {result['smart_size']:,} bytes")
        print(f"Compression ratio: {ratio:.2f}%")
        print(f"Success: {'✓' if result['success'] else '✗'}")
    
    # Removed cleanup to keep files

def create_assignment_test():
    """Create the specific test case mentioned in the assignment:
    0F AB BB pattern repeated 11 times (33 bytes total).
    """
    pattern = bytes([0x0F, 0xAB, 0xBB])  # 3-byte pattern
    repetitions = 11  # Total size will be 33 bytes
    filename = "assignment_test.bin"
    
    print(f"\nCreating Assignment test file: {filename}")
    print(f"Pattern: 0F AB BB")
    print(f"Pattern size: 3 bytes")
    print(f"Repetitions: {repetitions}")
    print(f"Total size: {3 * repetitions} bytes")
    
    create_test_file(filename, pattern, repetitions)
    
    # Test compression
    result = test_compression(filename)
    
    if result:
        ratio = (result['smart_size'] / result['original_size']) * 100
        print("\nResults:")
        print(f"Original size: {result['original_size']:,} bytes")
        print(f"Smart size: {result['smart_size']:,} bytes")
        print(f"Compression ratio: {ratio:.2f}%")
        print(f"Success: {'✓' if result['success'] else '✗'}")
    
    # Removed cleanup to keep files

def create_assignment_patterns_test(repetitions=11):
    """Create test files with the assignment pattern and 4 additional similar patterns.
    Each pattern is 3 bytes long to match the assignment pattern style.
    
    Args:
        repetitions: Number of times to repeat each pattern (default: 11)
    """
    test_patterns = [
        ("assignment_pattern.bin", bytes([0x0F, 0xAB, 0xBB]), "Assignment Pattern (0F AB BB)"),
        ("pattern_cafe.bin", bytes([0xCA, 0xFE, 0xEE]), "CAFE Pattern (CA FE EE)"),
        ("pattern_dead.bin", bytes([0xDE, 0xAD, 0xAD]), "DEAD Pattern (DE AD AD)"),
        ("pattern_ipv6.bin", bytes([0xFE, 0x80, 0x00]), "IPv6 Pattern (FE 80 00)"),
        ("pattern_babe.bin", bytes([0xBA, 0xBE, 0xEE]), "BABE Pattern (BA BE EE)")
    ]
    
    print(f"\n=== Testing Assignment-style Patterns ({repetitions} repetitions) ===")
    print("-" * 90)
    print(f"{'Pattern Type':<25} {'Pattern':<15} {'Size':<10} {'Smart':<10} {'Ratio':<8} {'Status'} {'Details'}")
    print("-" * 90)
    
    for filename, pattern, description in test_patterns:
        # Create test file
        create_test_file(filename, pattern, repetitions)
        original_size = len(pattern) * repetitions
        
        # Test compression
        result = test_compression(filename)
        
        if result:
            ratio = (result['smart_size'] / original_size) * 100
            status = "✓" if result['success'] else "✗"
            pattern_hex = ' '.join([f"{b:02X}" for b in pattern])
            details = f"{len(pattern)}B × {repetitions}"
            
            print(f"{description:<25} {pattern_hex:<15} {original_size:<10} "
                  f"{result['smart_size']:<10} {ratio:<8.2f}% {status}  {details}")
            
            # Analyze smart file if compression was successful
            if result['success']:
                smart_analysis = analyze_smart_file(f"{filename}.smart")
                if smart_analysis['is_pattern']:
                    print(f"    └─ Pattern-based compression: {smart_analysis['unique_data']} bytes unique data")
                else:
                    print(f"    └─ Block-based compression: {smart_analysis['unique_data']} bytes unique, "
                          f"{smart_analysis['sequence_data']} bytes sequence")
        
        # Keep the files for inspection
        if not result or not result['success']:
            print(f"Warning: Compression failed for {filename}")

def main():
    """Run the test suite with different repetition counts for the patterns."""
    # Test patterns with different repetition counts
    create_assignment_patterns_test(11)    # Original assignment case (33 bytes)
    create_assignment_patterns_test(100)   # Medium size test (300 bytes)
    create_assignment_patterns_test(1000)  # Larger size test (3000 bytes)
    
    # Test the special case from assignment (Case 2)
    print("\n=== Testing Case 2 (10-byte pattern × 100,000) ===")
    create_test_case2()

if __name__ == "__main__":
    main() 