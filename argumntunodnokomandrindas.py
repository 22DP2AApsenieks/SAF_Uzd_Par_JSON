#!/usr/bin/env python3
import argparse
import sys
import json
import os
from typing import List, Any

def enforce_json_extension(filename: str) -> str:
    """Ensures the output file ends with .json"""
    base, ext = os.path.splitext(filename)
    return f"{base}.json" if ext.lower() != '.json' else filename

def deep_merge_preserve_structure(data: List[Any]) -> List[Any]:
    """
    Preserves the original nested structure while removing duplicate objects.
    Duplicates are identified by both 'name' and 'value' matching.
    """
    seen_objects = set()
    result = []
    
    def process_level(level):
        if isinstance(level, list):
            new_level = []
            for item in level:
                processed = process_level(item)
                if processed is not None:
                    new_level.append(processed)
            return new_level if new_level else None
        elif isinstance(level, dict):
            obj_id = (level.get('name'), level.get('value'))
            if obj_id not in seen_objects:
                seen_objects.add(obj_id)
                return level
            return None
        return level
    
    for top_level_item in data:
        processed_item = process_level(top_level_item)
        if processed_item is not None:
            result.append(processed_item)
    
    return result

def get_json_files():
    """Get list of JSON files in current directory"""
    return [f for f in os.listdir() if f.endswith('.json')]

def select_files(files, action):
    """Let user select files for action"""
    print(f"\nAvailable JSON files ({len(files)}):")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")
    
    print(f"\nSelect files to {action} (e.g., '1 3 4') or 'all'")
    while True:
        choice = input("> ").strip().lower()
        if choice == 'all':
            return files
        try:
            selected = [files[int(i)-1] for i in choice.split()]
            return selected
        except (ValueError, IndexError):
            print("Error! Please try again")

def create_json():
    """Creates an empty JSON file with user-specified name"""
    while True:
        filename = input("Enter filename (without .json): ").strip()
        if not filename:
            print("Filename cannot be empty!")
            continue
            
        filename = f"{filename}.json" if not filename.endswith('.json') else filename
        
        if os.path.exists(filename):
            print(f"File '{filename}' already exists!")
            choice = input("Overwrite? (y/n): ").lower()
            if choice != 'y':
                continue
                
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4, ensure_ascii=False)
            print(f"Successfully created: {filename}")
            return
        except Exception as e:
            print(f"Error creating file: {e}")
            return

def try_load_json(file_path):
    """Try to load JSON file with different encodings"""
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'windows-1257', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in {file_path}: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error reading {file_path}: {e}")
            raise
    
    raise UnicodeDecodeError(f"Could not decode {file_path} with any of the tried encodings")

def merge_files_interactive():
    """Merge selected JSON files in interactive mode"""
    files = get_json_files()
    if not files:
        print("No JSON files found!")
        return
    
    selected = select_files(files, "merge")
    if not selected:
        print("No files selected!")
        return
    
    output_file = input("\nEnter output filename (default: merged.json): ").strip() or "merged.json"
    output_file = enforce_json_extension(output_file)
    
    combined = []
    for file in selected:
        try:
            file_data = try_load_json(file)
            if isinstance(file_data, list):
                combined.extend(file_data)
            else:
                combined.append(file_data)
            print(f"✓ {file}")
        except Exception as e:
            print(f"✕ Error reading {file}: {e}")
    
    merged_data = deep_merge_preserve_structure(combined)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully merged {len(combined)} files into {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

def delete_files():
    """Delete selected JSON files"""
    files = get_json_files()
    if not files:
        print("No JSON files found!")
        return
    
    selected = select_files(files, "delete")
    if not selected:
        print("No files selected!")
        return
    
    print("\nSelected files for deletion:")
    for f in selected:
        print(f"- {f}")
    
    confirm = input("\nAre you sure you want to delete these files? (y/n): ").lower()
    if confirm != 'y':
        print("Deletion cancelled!")
        return
    
    deleted = 0
    for file in selected:
        try:
            os.remove(file)
            print(f"Deleted {file}")
            deleted += 1
        except Exception as e:
            print(f"✕ Error deleting {file}: {e}")
    
    print(f"\nSuccessfully deleted {deleted} files")

def interactive_mode():
    """Run the program in interactive menu mode"""
    while True:
        print("\n=== JSON File Manager ===")
        print("1. Create new JSON file")
        print("2. Merge JSON files")
        print("3. Delete JSON files")
        print("4. Exit")
        
        choice = input("Choose operation (1-4): ").strip()
        
        if choice == '1':
            create_json()
        elif choice == '2':
            merge_files_interactive()
        elif choice == '3':
            delete_files()
        elif choice == '4':
            print("Program exiting. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice! Please enter 1, 2, 3 or 4")
        
        input("\nPress Enter to continue...")

def command_line_mode(args):
    """Run the program in command-line mode"""
    if args.command.lower() != 'merge':
        print(f"Warning: Unknown command '{args.command}'. Using 'merge' instead.", file=sys.stderr)
    
    output_file = enforce_json_extension(args.output)
    
    all_data = []
    for file in args.files:
        try:
            file_data = try_load_json(file)
            if isinstance(file_data, list):
                all_data.extend(file_data)
            else:
                all_data.append(file_data)
        except Exception as e:
            print(f"Error processing {file}: {e}", file=sys.stderr)
            sys.exit(1)
    
    merged_data = deep_merge_preserve_structure(all_data)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved merged data to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Merge JSON files while preserving nested structure.",
        usage="%(prog)s [-i] [-f file1.json file2.json] [-o output.json] [-c merge]"
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                       help="Run in interactive mode")
    parser.add_argument('-f', '--files', nargs='+',
                       help="Input JSON files to process (command-line mode only)")
    parser.add_argument('-o', '--output',
                       help="Output file name (command-line mode only)")
    parser.add_argument('-c', '--command', default='merge',
                       help="Operation to perform (default: merge)")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        if not args.files or not args.output:
            parser.print_help()
            print("\nError: In command-line mode, both -f and -o options are required", file=sys.stderr)
            sys.exit(1)
        command_line_mode(args)

if __name__ == "__main__":
    main()


    #notestet json formātus(ar dziļākiem iekšējiem objektiem). c = pievienot aizstāšanu // ko darīt ar dublējošiem failiem.