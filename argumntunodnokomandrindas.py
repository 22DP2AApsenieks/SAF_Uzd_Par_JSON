import argparse
import json
import os
import subprocess

def merge_json(files):
    """Merges data from multiple JSON files."""
    merged_data = []
    for file in files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.extend(data)  # Merge lists
        else:
            print(f"Warning: file {file} not found.")
    return merged_data

def sort_json(data):
    """Sorts data by the first key if it's a list of dictionaries."""
    if isinstance(data, list) and all(isinstance(i, dict) for i in data):
        sorted_data = sorted(data, key=lambda x: list(x.keys())[0])  # Sort by the first key
        return sorted_data
    else:
        print("Warning: Data is not a list of dictionaries.")
        return data

def filter_json(data, key, value):
    """Filters data by the specified key and value."""
    if isinstance(data, list):
        filtered_data = [item for item in data if item.get(key) == value]
        return filtered_data
    else:
        print("Warning: Data is not a list.")
        return data

def save_output(data, output_file):
    """Saves the processed data to the specified output file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to: {output_file}")

import subprocess

def run_apvieno_json_failus2():
    """Runs the 'apvieno_json_failus2.py' script."""
    print("Running 'apvieno_json_failus2.py'...")

    # Full path to 'apvieno_json_failus2.py'
    script_path = os.path.join(os.getcwd(), 'apvieno_json_failus2.py')  # Adjust path if necessary

    # If the script is located elsewhere, specify the full path here:
    # script_path = r"C:\path\to\your\script\apvieno_json_failus2.py"
    
    try:
        subprocess.run(['python', script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running 'apvieno_json_failus2.py': {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")  
        
def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Merge, sort, or filter JSON files.")
    parser.add_argument('-i', '--interactive', action='store_true', help="Run interactive program apvieno_json_failus2.py")
    parser.add_argument('-c', '--command', choices=['merge', 'sort', 'filter'], help="Choose operation: merge, sort, or filter")
    parser.add_argument('-f', '--files', nargs='+', help="List of input files")
    parser.add_argument('-o', '--output', help="Output file name")
    parser.add_argument('--key', help="Filter key (use only with 'filter' command)")
    parser.add_argument('--value', help="Filter value (use only with 'filter' command)")

    args = parser.parse_args()

    # If -i is specified, run the other program and exit
    if args.interactive:
        run_apvieno_json_failus2()
        return

    # Ensure the required arguments are provided based on the command
    if not args.command:
        print("Error: You must specify a command (-c merge, sort, or filter).")
        return
    if not args.output:
        print("Error: You must specify an output file (-o).")
        return

    # Execute the selected operation
    if args.command == 'merge':
        if not args.files:
            print("Error: Input files are required with '-f' option for merge.")
            return
        merged_data = merge_json(args.files)
        save_output(merged_data, args.output)

    elif args.command == 'sort':
        if not args.files:
            print("Error: Input files are required with '-f' option for sort.")
            return
        merged_data = merge_json(args.files)
        sorted_data = sort_json(merged_data)
        save_output(sorted_data, args.output)

    elif args.command == 'filter':
        if not args.key or not args.value:
            print("Error: Filter parameters ('--key' and '--value') are required for filter command.")
            return
        if not args.files:
            print("Error: Input files are required with '-f' option for filter.")
            return
        merged_data = merge_json(args.files)
        filtered_data = filter_json(merged_data, args.key, args.value)
        save_output(filtered_data, args.output)

if __name__ == '__main__':
    main()
