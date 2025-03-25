#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Any, Union, List, Dict, Set

# Constants
DEFAULT_OUTPUT = "merged.json"
SUPPORTED_COMMANDS = ['merge', 'overwrite', 'deepmerge']
JSON_EXTENSIONS = ('.json',)

def enforce_json_extension(filename: str) -> str:
    """Ensure filename ends with .json"""
    name, ext = os.path.splitext(filename)
    return f"{name}.json" if ext.lower() not in JSON_EXTENSIONS else filename

def get_json_files() -> List[str]:
    """Get list of JSON files in current directory"""
    return [f for f in os.listdir() if f.lower().endswith(JSON_EXTENSIONS)]

def load_json_file(file_path: str) -> Union[list, dict]:
    """Load JSON file with advanced encoding detection and error handling"""
    encodings = ['utf-8', 'utf-16', 'windows-1257', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise IOError(f"Error reading {file_path}: {e}")
    
    raise ValueError(f"Could not decode {file_path} with tried encodings")

def save_json(data: Any, filename: str) -> None:
    """Save data to JSON file with atomic write"""
    temp_file = f"{filename}.tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, filename)
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise e

def deep_merge(base: Any, new: Any, mode: str = 'merge') -> Any:
    """Enhanced deep merge with configurable strategies"""
    if mode == 'deepmerge':
        return _deep_merge_recursive(base, new)
    if mode == 'merge':
        return _merge_preserve(base, new)
    if mode == 'overwrite':
        return _merge_overwrite(base, new)
    return base

def _deep_merge_recursive(base: Any, new: Any) -> Any:
    """Deep merge strategy for complex nested structures"""
    if isinstance(base, dict) and isinstance(new, dict):
        merged = base.copy()
        for key, value in new.items():
            if key in merged:
                merged[key] = _deep_merge_recursive(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    if isinstance(base, list) and isinstance(new, list):
        return base + [item for item in new if item not in base]
    
    return new

def _merge_preserve(base: Any, new: Any) -> Any:
    """Merge preserving structure with duplicate detection"""
    if isinstance(base, dict) and isinstance(new, dict):
        merged = base.copy()
        for key, value in new.items():
            if key in merged:
                merged[key] = _merge_preserve(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    if isinstance(base, list) and isinstance(new, list):
        seen = _create_identity_set(base)
        merged = base.copy()
        for item in new:
            item_id = _get_item_identity(item)
            if item_id not in seen:
                merged.append(item)
                seen.add(item_id)
        return merged
    
    return new if _get_item_identity(base) != _get_item_identity(new) else base

def _merge_overwrite(base: Any, new: Any) -> Any:
    """Overwrite strategy with type preservation"""
    if isinstance(base, dict) and isinstance(new, dict):
        merged = base.copy()
        merged.update(new)
        return merged
    
    return new

def _get_item_identity(item: Any) -> str:
    """Create unique identifier for complex items"""
    if isinstance(item, (dict, list)):
        return json.dumps(item, sort_keys=True)
    return str(item)

def _create_identity_set(items: List[Any]) -> Set[str]:
    """Create set of identity hashes"""
    return {_get_item_identity(item) for item in items}

def interactive_selector(prompt: str, options: List[str]) -> List[str]:
    """Interactive selection of multiple options"""
    print(f"\n{prompt}:")
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
    
    while True:
        choices = input("Enter selections (comma-separated or 'all'): ").strip()
        if choices.lower() == 'all':
            return options
        
        try:
            indices = [int(idx.strip()) - 1 for idx in choices.split(',')]
            return [options[i] for i in indices]
        except (ValueError, IndexError):
            print("Invalid input. Please try again.")

def interactive_merge():
    """Enhanced interactive merging workflow"""
    files = get_json_files()
    if not files:
        print("No JSON files found in current directory.")
        return
    
    selected_files = interactive_selector("Available JSON files", files)
    if not selected_files:
        print("No files selected.")
        return
    
    output_file = input(f"\nEnter output filename (default: {DEFAULT_OUTPUT}): ").strip()
    output_file = enforce_json_extension(output_file or DEFAULT_OUTPUT)
    
    # Load existing data
    base_data = {}
    if os.path.exists(output_file):
        try:
            base_data = load_json_file(output_file)
            print(f"Loaded existing data from {output_file}")
        except Exception as e:
            print(f"Error loading existing file: {e}")
            if input("Continue without existing data? (y/n): ").lower() != 'y':
                return

    # Merge strategy selection
    strategies = {
        '1': ('merge', 'Combine data preserving existing structure'),
        '2': ('overwrite', 'Replace existing values with new data'),
        '3': ('deepmerge', 'Deep merge nested structures')
    }
    
    print("\nSelect merge strategy:")
    for key, (_, desc) in strategies.items():
        print(f"{key}. {desc}")
    
    strategy = strategies.get(input("Your choice (1-3): "), strategies['1'])[0]

    # Process files
    merged_data = base_data
    for file in selected_files:
        try:
            new_data = load_json_file(file)
            merged_data = deep_merge(merged_data, new_data, strategy)
            print(f"✓ Processed {file}")
        except Exception as e:
            print(f"✕ Error processing {file}: {e}")

    # Save result
    try:
        save_json(merged_data, output_file)
        print(f"\nSuccessfully saved merged data to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

def handle_command_line(args):
    """Command line interface handler"""
    output_file = enforce_json_extension(args.output)

    try:
        # Load or initialize base data
        base = load_json_file(output_file) if os.path.exists(output_file) else {}
        
        for file in args.files:
            new_data = load_json_file(file)
            base = deep_merge(base, new_data, args.command)
            print(f"Processed {file}")
        
        save_json(base, output_file)
        print(f"Successfully saved to {output_file}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Advanced JSON File Manager",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Merge strategies:\n"
               "  merge: Preserve structure, remove duplicates\n"
               "  overwrite: Replace existing values\n"
               "  deepmerge: Recursive merge of nested structures"
    )
    parser.add_argument('-i', '--interactive', action='store_true',
                       help="Run in interactive mode")
    parser.add_argument('-f', '--files', nargs='+',
                       help="Input files for command line mode")
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                       help=f"Output file name (default: {DEFAULT_OUTPUT})")
    parser.add_argument('-c', '--command', default='merge',
                       choices=SUPPORTED_COMMANDS,
                       help="Merge strategy to use")

    args = parser.parse_args()

    if args.interactive:
        interactive_merge()
    else:
        if not args.files:
            parser.print_help()
            print("\nError: Must specify files in command line mode", file=sys.stderr)
            sys.exit(1)
        handle_command_line(args)

if __name__ == "__main__":
    main()