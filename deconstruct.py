#!/usr/bin/env python3
import sys
import os
from typing import Dict, List, Tuple
import struct
from collections import defaultdict
import math

class SmartStorage:
    def __init__(self):
        self.unique_blocks = []
        self.block_sequence = []
        self.optimal_block_size = 0
        self.is_pattern_based = False
        self.pattern = None
        self.repetitions = 0

    def analyze_patterns(self, data: bytes, block_size: int) -> dict:
        """Analyze data for repeating patterns."""
        if len(data) == 0:
            return None
            
        pattern = data[:block_size]
        if len(data) % block_size == 0:
            is_repeating = True
            for i in range(0, len(data), block_size):
                if data[i:i + block_size] != pattern:
                    is_repeating = False
                    break
            if is_repeating:
                return {
                    'pattern': pattern,
                    'repetitions': len(data) // block_size,
                    'pattern_size': block_size
                }
        return None

    def process_file(self, filename: str) -> int:
        """Process file and return compressed size."""
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            if len(data) == 0:
                return 0

            # First check for patterns
            pattern_info = self.analyze_patterns(data, self.optimal_block_size)
            if pattern_info:
                self.is_pattern_based = True
                self.pattern = pattern_info['pattern']
                self.repetitions = pattern_info['repetitions']
                return 17 + len(self.pattern)  # Header (17 bytes) + pattern size
            
            # If no pattern found, use block-based approach
            self.is_pattern_based = False
            blocks = []
            block_map = {}
            
            for i in range(0, len(data), self.optimal_block_size):
                block = data[i:i + self.optimal_block_size]
                if block not in block_map:
                    block_map[block] = len(blocks)
                    blocks.append(block)
            
            self.unique_blocks = blocks
            self.block_sequence = [block_map[data[i:i + self.optimal_block_size]] 
                                 for i in range(0, len(data), self.optimal_block_size)]
            
            return (len(self.unique_blocks) * self.optimal_block_size +  # unique blocks
                   len(self.block_sequence) * 4 +                        # sequence indices
                   13)                                                   # header size

        except Exception as e:
            print(f"Error processing file: {e}", file=sys.stderr)
            return 0

    def write(self, filename: str):
        """Write the smart file."""
        try:
            with open(filename, 'wb') as f:
                if self.is_pattern_based:
                    # Write pattern-based format
                    f.write(bytes([0x01]))  # Format type
                    f.write(len(self.pattern).to_bytes(8, 'big'))  # Pattern size
                    f.write(self.repetitions.to_bytes(8, 'big'))   # Repetitions
                    f.write(self.pattern)                          # Pattern data
                else:
                    # Write block-based format
                    f.write(bytes([0x00]))  # Format type
                    f.write(self.optimal_block_size.to_bytes(8, 'big'))
                    f.write(len(self.unique_blocks).to_bytes(4, 'big'))
                    
                    # Write unique blocks
                    for block in self.unique_blocks:
                        f.write(block)
                    
                    # Write sequence
                    for index in self.block_sequence:
                        f.write(index.to_bytes(4, 'big'))
                        
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)

def analyze_pattern(data, block_size):
    """Analyze data for repeating patterns."""
    if len(data) == 0:
        return None
        
    # Look for repeating pattern
    for pattern_size in range(block_size, len(data) + 1):
        pattern = data[:pattern_size]
        # Check if this pattern repeats throughout the file
        if len(data) % pattern_size == 0:  # Must be evenly divisible
            is_repeating = True
            for i in range(0, len(data), pattern_size):
                if data[i:i + pattern_size] != pattern:
                    is_repeating = False
                    break
            if is_repeating:
                repetitions = len(data) // pattern_size
                return {
                    'pattern': pattern,
                    'repetitions': repetitions,
                    'pattern_size': pattern_size
                }
    return None

def write_smart_file(input_file: str, block_size: int, output_file: str):
    """Write the smart file with optimized format."""
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Check for repeating pattern first
    pattern_info = analyze_pattern(data, block_size)
    
    with open(output_file, 'wb') as f:
        if pattern_info:
            # Write pattern-based format
            f.write(bytes([0x01]))  # Format type: pattern
            f.write(pattern_info['pattern_size'].to_bytes(8, 'big'))
            f.write(pattern_info['repetitions'].to_bytes(8, 'big'))
            f.write(pattern_info['pattern'])
        else:
            # Write block-based format
            f.write(bytes([0x00]))  # Format type: blocks
            f.write(block_size.to_bytes(8, 'big'))
            f.write(len(data).to_bytes(8, 'big'))
            
            blocks = []
            block_map = {}
            
            for i in range(0, len(data), block_size):
                block = data[i:i + block_size]
                if block not in block_map:
                    block_map[block] = len(blocks)
                    blocks.append(block)
            
            # Write blocks and sequence
            f.write(len(blocks).to_bytes(4, 'big'))
            for block in blocks:
                f.write(block)
            
            # Write sequence
            for i in range(0, len(data), block_size):
                block = data[i:i + block_size]
                index = block_map[block]
                f.write(index.to_bytes(4, 'big'))

def main():
    if len(sys.argv) != 3:
        print("Usage: ./deconstruct <filename> <block_size>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    block_size = int(sys.argv[2])
    
    storage = SmartStorage()
    storage.optimal_block_size = block_size
    size = storage.process_file(input_file)
    storage.write(f"{input_file}.smart")
    print(size)

if __name__ == "__main__":
    main() 