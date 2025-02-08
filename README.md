# Smart File Storage System

## Key Solutions Implemented

### 1. Pattern Repetition Case (Case 2 from Assignment)
Successfully solved the case where 10 bytes are repeated 100,000 times:
- Input: 10-byte pattern repeated 100,000 times (would normally require 1MB storage)
- Output: Only 10 bytes stored (If including minimal metadata smartfile size maybe 20 - 30 bytes rather than 1000000 bytes. still a good deal)
- Achievement: Reduced storage from 1MB to essentially 10 bytes
- Test Implementation: `create_case2_test()` in test suite

### 2. Basic Pattern Test Case
Successfully implemented the example from assignment:
- Pattern: `0F AB BB` (3 bytes)
- Repetitions: 11 times
- Total Original Size: 33 bytes
- Compressed: Stores only 3 bytes (If including minimal metadata smartfil size maybe 20 bytes still saves some space. This happens only when the repetetions of the data is so low. technically works with large duplicate data very very effieciently.)
- Test Implementation: `create_basic_pattern_test()` in test suite

## System Overview

### Core Functionality
1. **Deconstruct Program** (`./deconstruct`)
   - Input: `<filename> <block_size>`
   - Detects repeated blocks
   - Outputs minimum required storage bytes
   - Creates compressed smart file

2. **Reconstruct Program** (`./reconstruct`)
   - Rebuilds original file from compressed format
   - Uses metadata to reconstruct exact original


## Usage

```bash
# Compression
./deconstruct <input_file> <block_size>

# Decompression
./reconstruct <input_file> <output_file>
```

## Test Suite (check the bottom of this page to learn how to run these test suites)
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

## Design Considerations

### Strengths
1. Efficiently handles repeated patterns
2. Fixed block size as per assignment requirements
3. Non-sliding block boundaries
4. Minimal metadata overhead

### Limitations
1. Block size must be specified
   - Example: If a file has a repeating pattern of 7 bytes but block_size is set to 4,
     the pattern won't be detected efficiently:
     ```
     File content: AA BB CC DD AA BB CC DD AA BB CC DD
     With block_size=4:
     Block1: AA BB CC DD (stored)
     Block2: AA BB CC DD (stored again as different block)
     Block3: AA BB CC DD (stored again as different block)
     ```

2. Non-sliding windows might miss some patterns
   - Example: With fixed boundaries, overlapping patterns are missed:
     ```
     File content: AB CD EF AB CD EF AB CD EF
     With block_size=4:
     Block1: AB CD (stored)
     Block2: EF AB (stored)
     Block3: CD EF (stored)
     ```
   - A sliding window could have detected the repeating "AB CD EF" pattern

3. Small files might have metadata overhead
   - Example: For a 10-byte file:
     ```
     Original file size: 10 bytes
     Metadata required: 13 bytes
       - Format identifier: 1 byte
       - Block size: 8 bytes
       - Number of blocks: 4 bytes
     Total storage: 23 bytes (larger than original)
     ```

## Implementation Notes
- Blocks are created at exact boundaries (non-sliding)
- Block size is fixed based on input parameter
- Example: With block size 4, bytes 0-3 = block 1, bytes 4-7 = block 2, etc.
- Metadata is added for reconstruction purposes

## Running Tests (Don't get tired of manual test use these two in-depth tests with various bunch of examples)
```bash
python create_test.py   # Includes Case 2, the example file you gave in assignment and basic pattern tests.

python complex_test.py 
```

```bash complex_text.py``` - This creates a total of 100 different test files with varying:
Pattern sizes (1 to 64 bytes)
Repetition counts (50 to 1000)
Pattern complexity (simple to complex)
Mathematical relationships (increments, XOR, modulo)
Each pattern is designed to test different aspects of the compression algorithm's capabilities in handling:
Simple repetitions
Sequential patterns
Alternating patterns
Mathematical patterns
Mixed patterns
Various file sizes

## Source Code
Repository: [GitHub Repository](https://github.com/iamvaar-dev/port_first_round)
