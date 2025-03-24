import json
import os
import sys

def interactive_mode():
    def show_menu():
        """Display main menu and get user choice"""
        print("\n=== JSON File Manager ===")
        print("1. Izveidot jaunu JSON failu")
        print("2. Apvienot JSON failus")
        print("3. Izdzēst JSON failus")
        print("4. Iziet")
        
        while True:
            choice = input("Izvēlies darbību (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            print("Nepareiza ievade! Lūdzu ievadi 1, 2, 3 vai 4")

    def get_json_files():
        """Get list of JSON files in current directory"""
        return [f for f in os.listdir() if f.endswith('.json')]

    def select_files(files, action):
        """Let user select files for action"""
        print(f"\nPieejamie JSON faili ({len(files)}):")
        for i, f in enumerate(files, 1):
            print(f"{i}. {f}")
        
        print(f"\nIzvēlies failus ko {action} (piem., '1 3 4') vai 'visu'")
        while True:
            choice = input("> ").strip().lower()
            if choice == 'visu':
                return files
            try:
                selected = [files[int(i)-1] for i in choice.split()]
                return selected
            except (ValueError, IndexError):
                print("Kļūda! Ievadiet vēlreiz")

    def create_json():
        """Creates an empty JSON file with user-specified name"""
        while True:
            # Get filename input
            vards = input("Ievadi faila nosaukumu (bez .json): ").strip()
            if not vards:
                print("Nosaukums nevar būt tukšs!")
                continue
                
            # Add .json extension if not present
            filename = f"{vards}.json" if not vards.endswith('.json') else vards
            
            # Check if file exists
            if os.path.exists(filename):
                print(f"Fails '{filename}' jau eksistē!")
                choice = input("Vai pārrakstīt? (y/n): ").lower()
                if choice != 'y':
                    continue
                    
            # Create the file
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=4, ensure_ascii=False)
                print(f"Veiksmīgi izveidots: {filename}")
                return
            except Exception as e:
                print(f"Kļūda izveidojot failu: {e}")
                return


    def merge_files():
        """Merge selected JSON files"""
        files = get_json_files()
        if not files:
            print("Nav atrasts neviens JSON fails!")
            return
        
        selected = select_files(files, "apvienot")
        if not selected:
            print("Nav izvēlēts neviens fails!")
            return
        
        output_file = input("\nIevadi izvades faila nosaukumu (default: merged.json): ").strip() or "merged.json"
        if not output_file.endswith('.json'):
            output_file += '.json'
        
        combined = []
        for file in selected:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    combined.append(json.load(f))
                print(f"✓ {file}")
            except Exception as e:
                print(f"✕ Kļūda lasot {file}: {e}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        print(f"\nVeiksmīgi apvienoti {len(combined)} faili uz {output_file}")

    def delete_files():
        """Delete selected JSON files"""
        files = get_json_files()
        if not files:
            print("Nav atrasts neviens JSON fails!")
            return
        
        selected = select_files(files, "izdzēst")
        if not selected:
            print("Nav izvēlēts neviens fails!")
            return
        
        print("\nIzvēlētie faili dzēšanai:")
        for f in selected:
            print(f"- {f}")
        
        confirm = input("\nVai tiešām vēlies dzēst šos failus? (y/n): ").lower()
        if confirm != 'y':
            print("Dzēšana atcelta!")
            return
        
        deleted = 0
        for file in selected:
            try:
                os.remove(file)
                print(f"izdzēsts {file}")
                deleted += 1
            except Exception as e:
                print(f"✕ Kļūda dzēšot {file}: {e}")
        
        print(f"\nVeiksmīgi izdzēsti {deleted} faili")

    def main():
        while True:
            choice = show_menu()
            
        
            """if choice == '1':
                create_json()
            elif choice == '2':
                merge_files()
            elif choice == '3':
                delete_files()
            elif choice == '4':
                print("Programma beidza darbu. Uz redzēšanos!")
                sys.exit()"""
            
            input("\nNospied Enter, lai turpinātu...")

    if __name__ == "__main__":
        main()

    # -i(nteractive) -h(help) -c(opcijas) -f(faili=input) -o(output)

    #./merge.py -i -f file1.json file2.json file3.json -o output.json -c merge
    #argumentu nodošana no komandrindas