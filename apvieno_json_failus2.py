import json
import os

# Simple JSON Merger
# Merges all JSON files in current directory into merged_output.json

def main():
    # Find all JSON files (excluding our output file) f=file
    json_files = [
        f for f in os.listdir() 
        if f.endswith('.json') 
        and f != 'merged_output.json'
    ]

    if not json_files:
        print("No JSON files found to merge!")
        return

    # Load and combine all data
    combined = []
    for filename in json_files:
        try:
            with open(filename, 'r') as f:
                combined.append(json.load(f))
            print(f"Added: {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")

    # Save combined data
    with open('merged_output.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\nSuccessfully merged {len(combined)} files into merged_output.json")

if __name__ == "__main__":
    main()

    #kur saglabāt, kurus saglabā, kā saglabāt (aizstāt, uzlabot, mainīt)