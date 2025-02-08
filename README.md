# Pattern-Based File Compression System Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Key Test Cases](#key-test-cases)
4. [Compression Algorithms](#compression-algorithms)
5. [File Formats](#file-formats)
6. [Test Suites](#test-suites)
7. [Usage Guide](#usage-guide)
8. [Performance Analysis](#performance-analysis)
9. [Implementation Details](#implementation-details)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

## Overview

This system implements a pattern-based file compression solution with two main compression strategies:
- Pattern-based compression for repeating sequences
- Block-based compression for files with unique blocks

### Key Test Cases Solved
1. **Case 2 Solution**: Successfully handles 10-byte patterns repeated 100,000 times
   - Instead of storing 1MB of data
   - Compressed using pattern-based approach
   - Significant storage optimization achieved

2. **File Fill Pattern Test**: Demonstrates basic pattern repetition
   - Pattern: `0F AB BB` (3 bytes)
   - Repeated 11 times
   - Total size: 33 bytes
   - Efficiently compressed using pattern detection

### Key Features
- Automatic pattern detection
- Efficient block-based compression fallback
- Comprehensive test suite
- File integrity verification
- Detailed compression analytics

## System Architecture

### Core Components
1. **Deconstruct (Compression)**
   - Pattern analysis
   - Block identification
   - Smart file generation

2. **Reconstruct (Decompression)**
   - Format detection
   - Pattern reconstruction
   - Block sequence rebuilding

3. **Testing Framework**
   - Simple pattern tests
   - Complex pattern tests
   - Performance benchmarks

## Compression Algorithms

### 1. Pattern-Based Compression
```python
Format: [0x01][Pattern Size (8B)][Repetitions (8B)][Pattern Data]
```
- Identifies repeating patterns
- Optimal for files with regular repetitions
- Header size: 17 bytes

### 2. Block-Based Compression
```python
Format: [0x00][Block Size (8B)][Num Blocks (4B)][Unique Blocks][Sequence Data]
```
- Identifies unique blocks
- Maintains sequence information
- Optimal for files with recurring blocks

## File Formats

### Smart File Structure
1. **Pattern Format (0x01)**
   - 1 byte: Format type
   - 8 bytes: Pattern size
   - 8 bytes: Repetitions
   - N bytes: Pattern data

2. **Block Format (0x00)**
   - 1 byte: Format type
   - 8 bytes: Block size
   - 4 bytes: Number of blocks
   - N bytes: Block data
   - M bytes: Sequence data

## Test Suites

### 1. Simple Test Suite (create_test.py)
```python
# Key Test Case 2 Implementation
def create_case2_test():
    """Creates a test file with 10-byte pattern repeated 100,000 times"""
    pattern = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A])
    create_test_file("case2_test.bin", pattern, 100000)  # Creates 1MB file

# Basic Pattern Fill Test
def create_basic_pattern_test():
    """Creates a test file with 3-byte pattern repeated 11 times"""
    pattern = bytes([0x0F, 0xAB, 0xBB])
    create_test_file("basic_pattern.bin", pattern, 11)  # Creates 33-byte file
```

#### Test Categories:
1. Assignment Pattern Tests (3-byte patterns)
2. Special Case Tests (10-byte patterns)
3. Repetition Tests (11, 100, 1000 repetitions)

### 2. Complex Test Suite (complex_test.py)

#### A. Simple Patterns (10 tests)
```python
[(f"simple_{i}.bin", bytes([i]), 1000, f"Single byte 0x{i:02X}")
 for i in range(10)]
```

#### B. Small Patterns (20 tests)
```python
# 3-byte patterns
[(f"small_{i}.bin", bytes([i, i+1, i+2]), 500, f"3-byte increment {i}")
 for i in range(10)]
# 4-byte patterns
[(f"small_alt_{i}.bin", bytes([0xFF, i, 0x00, i]), 500, f"4-byte alternating {i}")
 for i in range(10)]
```

#### C. Medium Patterns (20 tests)
```python
# 8-byte sequences
[(f"med_{i}.bin", bytes(range(i, i+8)), 200, f"8-byte sequence {i}")
 for i in range(10)]
# 16-byte sequences
[(f"med_rev_{i}.bin", bytes(range(15-i, 15-i+16)), 200, f"16-byte reverse {i}")
 for i in range(10)]
```

#### D. Large Patterns (20 tests)
```python
# 32-byte patterns
[(f"large_{i}.bin", bytes([x % (i+1) for x in range(32)]), 100, f"32-byte mod{i+1}")
 for i in range(10)]
# 64-byte patterns
[(f"large_comp_{i}.bin", bytes([i ^ x for x in range(64)]), 50, f"64-byte XOR {i}")
 for i in range(10)]
```

#### E. Complex Patterns (30 tests)
```python
# Alternating patterns
[(f"complex_{i}.bin", 
  bytes([x if x % 2 == 0 else 255-x for x in range(16)]) * (i+1),
  100, f"Complex alternating {i}")
 for i in range(10)]
# Repeating patterns
[(f"complex_rep_{i}.bin",
  bytes([i, i*2, i*3, 0xFF, 0xAA]) * (i+2),
  200, f"Complex repeating {i}")
 for i in range(10)]
# Mixed patterns
[(f"complex_mix_{i}.bin",
  bytes([x ^ (i*8) for x in range(24)]) + bytes([0xAA, 0xBB, 0xCC] * i),
  150, f"Complex mixed {i}")
 for i in range(10)]
```

## Usage Guide

### 1. Basic Usage
```bash
# Compression
./deconstruct <input_file> <block_size>

# Decompression
./reconstruct <input_file> <output_file>

# Running Tests
python create_test.py    # Simple pattern tests
python complex_test.py   # Complex pattern tests
```

### 2. Test Suite Execution
```bash
# Run all tests
python create_test.py

# Run specific test cases
python complex_test.py
```

## Performance Analysis

### Metrics Tracked
1. Compression Ratio
2. Success Rate
3. Pattern Distribution
4. File Size Impact

### Analysis Reports
```
=== Compression Analysis Report ===
- Total tests
- Success rate
- Average compression ratio
- Best/Worst compression cases
- Ratio distribution
- Failed compression analysis
```

## Implementation Details

### 1. Pattern Detection (SmartStorage class)
```python
def analyze_patterns(self, data: bytes, block_size: int) -> dict:
    """
    Analyzes data for repeating patterns
    Returns pattern information if found
    """
```

### 2. Block Processing
```python
def process_file(self, filename: str) -> int:
    """
    Processes file using either pattern or block-based compression
    Returns compressed size
    """
```

### 3. File Writing
```python
def write(self, filename: str):
    """
    Writes compressed data in smart format
    Handles both pattern and block-based formats
    """
```

## Examples

### 1. Simple Pattern Compression
```python
# Example: 3-byte pattern repeated 11 times
pattern = bytes([0x0F, 0xAB, 0xBB])
repetitions = 11
create_test_file("example.bin", pattern, repetitions)
```

### 2. Complex Pattern Test
```python
# Example: 16-byte alternating pattern
pattern = bytes([x if x % 2 == 0 else 255-x for x in range(16)])
create_test_file("complex.bin", pattern, 100)
```

## Troubleshooting

### Common Issues
1. **Compression Failures**
   - Check file permissions
   - Verify input file exists
   - Ensure sufficient disk space

2. **Pattern Detection Issues**
   - Verify file size > pattern size
   - Check for file corruption
   - Validate block size parameter

### Error Messages
```python
"Error processing file: {e}"
"Error writing file: {e}"
"Compression failed for {filename}"
```

---

## Additional Resources
- Source code: [GitHub Repository](https://github.com/iamvaar-dev/port_first_round)
- Test files: They will be generated in the present working directory
- Performance logs: Generated during test execution
