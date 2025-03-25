#!/usr/bin/env python3
import argparse
import json
import os
import sys
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
    """Merge data while handling lists and dicts"""
    if mode == 'merge':
        return _merge_preserve(base, new)
    elif mode == 'overwrite':
        return _merge_overwrite(base, new)
    return base

def _merge_preserve(base: Any, new: Any) -> Any:
    """Merge lists and dicts while preserving unique entries"""
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
    """Overwrite base data with new data"""
    if isinstance(base, dict) and isinstance(new, dict):
        merged = base.copy()
        for key, value in new.items():
            merged[key] = value
        return merged
    
    if isinstance(base, list) and isinstance(new, list):
        return new  # Overwrite the list entirely
    
    return new

def copy_file(source: str, destination: str) -> None:
    """Copy content from source file to destination file"""
    try:
        data = load_json_file(source)
        save_json(data, destination)
        print(f"Successfully copied {source} to {destination}")
    except Exception as e:
        print(f"Error copying {source} to {destination}: {e}")

def interactive_merge():
    """Interactive merging workflow with user prompts."""
    files = get_json_files()
    if not files:
        print("No JSON files found in the current directory.")
        return

    print("Available JSON files:")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file}")

    try:
        file_indices = input("\nEnter input files separated by commas (e.g., 1,3): ")
        selected_indices = [int(idx.strip()) - 1 for idx in file_indices.split(',')]
        selected_files = [files[idx] for idx in selected_indices]
    except (ValueError, IndexError):
        print("Invalid selection. Please ensure you enter valid numbers corresponding to the files.")
        return

    print("\nSelect the operation:")
    print("1. Merge (combine)")
    print("2. Overwrite (replace existing data with new data)")
    try:
        operation_choice = int(input("Enter 1 or 2: "))
        if operation_choice == 1:
            mode = 'merge'
        elif operation_choice == 2:
            mode = 'overwrite'
        else:
            print("Invalid choice. Defaulting to 'merge'.")
            mode = 'merge'
    except ValueError:
        print("Invalid input. Defaulting to 'merge'.")
        mode = 'merge'

    output_file = input(f"\nEnter output filename (default: {DEFAULT_OUTPUT}): ").strip()
    output_file = enforce_json_extension(output_file or DEFAULT_OUTPUT)

    # Load existing data if the output file exists
    combined = []
    if os.path.exists(output_file):
        try:
            existing_data = load_json_file(output_file)
            if isinstance(existing_data, list):
                combined.extend(existing_data)
            elif isinstance(existing_data, dict):
                combined.append(existing_data)
            print(f"Loaded existing data from {output_file}")
        except Exception as e:
            print(f"Error loading existing file: {e}")

    # Load and merge selected files
    for file in selected_files:
        try:
            file_data = load_json_file(file)
            if isinstance(file_data, list):
                combined.extend(file_data)
            elif isinstance(file_data, dict):
                combined.append(file_data)
            print(f"✓ Loaded {file}")
        except Exception as e:
            print(f"✕ Error reading {file}: {e}")

    # Remove duplicates if merging
    if mode == 'merge':
        seen = set()
        merged = []
        for item in combined:
            item_hash = json.dumps(item, sort_keys=True)
            if item_hash not in seen:
                seen.add(item_hash)
                merged.append(item)
        combined = merged

    # Save the merged data
    try:
        save_json(combined, output_file)
        print(f"\nSuccessfully saved merged data to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")


def handle_command_line(args):
    """Handle command line mode for merge, overwrite, or copy"""
    output_file = enforce_json_extension(args.output)

    if args.command == "copy":
        if len(args.files) != 2:
            print("Error: You must provide exactly 2 files for the copy command.")
            sys.exit(1)
        source, destination = args.files
        copy_file(source, destination)
    else:
        # Load or initialize base data
        try:
            if os.path.exists(output_file):
                base = load_json_file(output_file)
                if not isinstance(base, (list, dict)):
                    raise ValueError("Existing file must be JSON list or object")
            else:
                base = []
        except Exception as e:
            print(f"Error loading existing file: {e}", file=sys.stderr)
            sys.exit(1)

        for file in args.files:
            try:
                new_data = load_json_file(file)
                base = deep_merge(base, new_data, args.command)
                print(f"Processed {file}")
            except Exception as e:
                print(f"Error processing {file}: {e}", file=sys.stderr)
                sys.exit(1)

        try:
            save_json(base, output_file)
            print(f"Successfully saved to {output_file}")
        except Exception as e:
            print(f"Save failed: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="JSON File Manager with merge/overwrite/copy capabilities",
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
