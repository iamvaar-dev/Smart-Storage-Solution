#!/usr/bin/env python3
import sys
import struct

def reconstruct_file(input_file: str, output_file: str):
    """Reconstruct the original file from the smart format."""
    with open(input_file, 'rb') as f:
        # Read format type
        format_type = int.from_bytes(f.read(1), 'big')
        
        if format_type == 0x01:  # Pattern-based format
            # Read pattern size and repetitions
            pattern_size = int.from_bytes(f.read(8), 'big')
            repetitions = int.from_bytes(f.read(8), 'big')
            pattern = f.read(pattern_size)
            
            # Write repeated pattern
            with open(output_file, 'wb') as out:
                for _ in range(repetitions):
                    out.write(pattern)
        else:  # Block-based format
            # Read block size and number of blocks
            block_size = int.from_bytes(f.read(8), 'big')
            num_blocks = int.from_bytes(f.read(4), 'big')
            
            # Read blocks
            blocks = []
            for _ in range(num_blocks):
                blocks.append(f.read(block_size))
            
            # Read and process sequence
            with open(output_file, 'wb') as out:
                while True:
                    index_bytes = f.read(4)
                    if not index_bytes:
                        break
                    index = int.from_bytes(index_bytes, 'big')
                    out.write(blocks[index])

def main():
    if len(sys.argv) != 3:
        print("Usage: ./reconstruct <input_file> <output_file>", file=sys.stderr)
        sys.exit(1)
    
    reconstruct_file(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main() 