#!/usr/bin/env python3
import argparse
import sys
import json
import os
from typing import Any, Union, List, Dict

# Constants
DEFAULT_OUTPUT = "merged.json"
SUPPORTED_COMMANDS = ['merge', 'overwrite']
JSON_EXTENSIONS = ('.json',)

def enforce_json_extension(filename: str) -> str:
    """Ensure filename ends with .json"""
    name, ext = os.path.splitext(filename)
    return f"{name}.json" if ext.lower() not in JSON_EXTENSIONS else filename

def get_json_files() -> List[str]:
    """Get list of JSON files in current directory"""
    return [f for f in os.listdir() if f.lower().endswith(JSON_EXTENSIONS)]

def load_json_file(file_path: str) -> Union[list, dict]:
    """Load JSON file with automatic encoding detection"""
    encodings = ['utf-8', 'utf-16', 'windows-1257', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(f"Could not decode {file_path}")

def save_json(data: Any, filename: str) -> None:
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def deep_merge(base: Any, new: Any, mode: str = 'merge') -> Any:
    """
    Unified deep merge function for both modes
    - mode='merge': Remove duplicates while preserving structure
    - mode='overwrite': Recursively overwrite values
    """
    if mode == 'merge':
        return _merge_preserve(base, new)
    return _merge_overwrite(base, new)

def _merge_preserve(base: Any, new: Any) -> Any:
    """Merge preserving structure and removing duplicates"""
    if isinstance(base, list) and isinstance(new, list):
        seen = {json.dumps(item, sort_keys=True) for item in base}
        merged = base.copy()
        
        for item in new:
            item_str = json.dumps(item, sort_keys=True)
            if item_str not in seen:
                merged.append(item)
                seen.add(item_str)
        return merged
    
    if isinstance(base, dict) and isinstance(new, dict):
        merged = base.copy()
        for key, value in new.items():
            if key in merged:
                merged[key] = _merge_preserve(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    return new if isinstance(base, type(new)) else base

def _merge_overwrite(base: Any, new: Any) -> Any:
    """Recursively overwrite values in base with new values"""
    if isinstance(base, dict) and isinstance(new, dict):
        merged = base.copy()
        for key, value in new.items():
            merged[key] = _merge_overwrite(merged.get(key), value)
        return merged
    
    if isinstance(base, list) and isinstance(new, list):
        return base + new  # Or replace with new for full overwrite
    
    return new

def interactive_merge():
    """Interactive merging workflow"""
    files = get_json_files()
    if not files:
        print("No JSON files found!")
        return
    
    selected = select_files(files, "merge")
    if not selected:
        print("No files selected!")
        return
    
    output_file = input(f"\nEnter output filename (default: {DEFAULT_OUTPUT}): ").strip()
    output_file = enforce_json_extension(output_file or DEFAULT_OUTPUT)
    
    combined = []
    if os.path.exists(output_file):
        try:
            combined.append(load_json_file(output_file))
            print(f"Loaded existing {output_file}")
        except Exception as e:
            print(f"Error loading existing file: {e}")
    
    for file in selected:
        try:
            combined.append(load_json_file(file))
            print(f"✓ {file}")
        except Exception as e:
            print(f"✕ Error reading {file}: {e}")
    
    merged = combined[0]
    for data in combined[1:]:
        merged = deep_merge(merged, data, 'merge')
    
    try:
        save_json(merged, output_file)
        print(f"Successfully saved to {output_file}")
    except Exception as e:
        print(f"Save failed: {e}")

def handle_command_line(args):
    """Command line mode processor"""
    output_file = enforce_json_extension(args.output)
    
    # Load or initialize base data
    try:
        base = load_json_file(output_file) if os.path.exists(output_file) else []
    except Exception as e:
        print(f"Error loading existing file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process input files
    for file in args.files:
        try:
            new_data = load_json_file(file)
            base = deep_merge(base, new_data, args.command)
            print(f"Processed {file}")
        except Exception as e:
            print(f"Error processing {file}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Save result
    try:
        save_json(base, output_file)
        print(f"Successfully saved to {output_file}")
    except Exception as e:
        print(f"Save failed: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="JSON File Manager with merge/overwrite capabilities",
        usage="%(prog)s [-i] [-f FILES...] [-o OUTPUT] [-c COMMAND]"
    )
    parser.add_argument('-i', '--interactive', action='store_true',
                       help="Run in interactive mode")
    parser.add_argument('-f', '--files', nargs='+',
                       help="Input files for command line mode")
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                       help=f"Output file name (default: {DEFAULT_OUTPUT})")
    parser.add_argument('-c', '--command', default='merge',
                       choices=SUPPORTED_COMMANDS,
                       help="Operation mode (default: merge)")
    
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