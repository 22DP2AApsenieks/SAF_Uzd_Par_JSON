#!/usr/bin/env python3
import argparse
import json
import os
import sys
from collections.abc import MutableMapping

def merge_json(a, b):
    """
    Rekursīvi apvieno divus JSON objektus/dictionaries.
    - Dziļi apvieno vārdnīcas
    - Apvieno sarakstus, izvairoties no dublikātiem
    - Saglabā esošos datus, ja struktūras nesakrīt
    """
    if isinstance(a, MutableMapping) and isinstance(b, MutableMapping):
        result = a.copy()
        for key, value in b.items():
            if key in result:
                result[key] = merge_json(result[key], value)
            else:
                result[key] = value
        return result
    elif isinstance(a, list) and isinstance(b, list):
        # Pārbauda dublikātus pēc satura (nevis atsauces)
        existing = {json.dumps(item, sort_keys=True) for item in a}
        combined = a.copy()
        for item in b:
            if json.dumps(item, sort_keys=True) not in existing:
                combined.append(item)
        return combined
    else:
        # Saglabā esošos datus, ja tipi nesakrīt
        return a if a is not None else b

def process_command_line(args):
    """Apstrādā komandrindas argumentus"""
    # Validācija pirms apstrādes
    if not os.path.exists(args.input):
        print(f"KĻŪDA: Ievades fails {args.input} neeksistē!")
        sys.exit(1)

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data_input = json.load(f)
    except Exception as e:
        print(f"KĻŪDA: Nevarēja nolasīt {args.input}: {str(e)}")
        sys.exit(1)

    if args.operation.lower() == "merge":
        # Ielādē esošos datus, ja fails eksistē
        data_output = {}
        if os.path.exists(args.output):
            try:
                with open(args.output, "r", encoding="utf-8") as f:
                    data_output = json.load(f)
            except Exception as e:
                print(f"Brīdinājums: Nevarēja ielādēt {args.output}: {str(e)}")
                print("Turpinām ar tukšu bāzi...")
        
        merged = merge_json(data_output, data_input)
        
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=4, ensure_ascii=False) #f=izvelata faila obj
                f.flush()  # Piespiež rakstīšanu buferī
                os.fsync(f.fileno())  # Piespiež rakstīšanu diskā
            print(f"APVIENOŠANA VEIKSMĪGA: {args.input} uz {args.output}")
        except Exception as e:
            print(f"KĻŪDA: Nevarēja saglabāt {args.output}: {str(e)}")
            sys.exit(1)

    elif args.operation.lower() == "overwrite":
        # PILNĪGA PĀRRAKSTĪŠANA ar papildu validāciju
        try:
            # Pārbauda, vai ievade ir derīgs JSON objekts
            if not isinstance(data_input, (dict, list)):
                print("KĻŪDA: Ievadei jābūt JSON objektam vai masīvam!")
                sys.exit(1)
                
            with open(args.output, "w", encoding="utf-8", errors="strict") as f:
                json.dump(data_input, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            print(f"PĀRRAKSTĪŠANA VEIKSMĪGA: {args.input} → {args.output}")
            
            # Pārbauda, vai fails faktiski tika ierakstīts
            if os.path.getsize(args.output) == 0:
                print("BRĪDINĀJUMS: Izvades fails ir tukšs!")
        except Exception as e:
            print(f"KĻŪDA: Neizdevās pārrakstīt {args.output}: {str(e)}")
            sys.exit(1)

def list_json_files():
    """Atgriež .json failu sarakstu pašreizējā direktorijā"""
    return [f for f in os.listdir(".") 
            if f.endswith(".json") and os.path.isfile(f)]

def interactive_mode():
    """Interaktīvais režīms"""
    while True:
        print("\n=== JSON RĪKS ===")
        print("1. Izveidot JSON")
        print("2. Apvienot JSON")
        print("3. Izdzēst JSON")
        print("4. Iziet")
        
        choice = input("Izvēle (1-4): ").strip()
        
        if choice == "1":
            files = list_json_files()
            if files:
                print("\nEsošie faili:")
                for i, f in enumerate(files, 1):
                    print(f"{i}. {f}")
                    
            filename = input("\nJauna faila nosaukums: ").strip()
            if not filename.endswith(".json"):
                filename += ".json"
                
            try:
                content = input("JSON saturs (tukšs = {}): ").strip() or "{}"
                data = json.loads(content)
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"Fails {filename} izveidots!")
            except Exception as e:
                print(f"Kļūda: {str(e)}")

        elif choice == "2":
            files = list_json_files()
            if len(files) < 2:
                print("Nepietiek failu!")
                continue
                
            print("\nPieejamie faili:")
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
                
            try:
                src_idx = int(input("Izvēlies avota failu (nr): ")) - 1
                dst_idx = int(input("Izvēlies mērķa failu (nr): ")) - 1
                src_file = files[src_idx]
                dst_file = files[dst_idx]
                
                with open(src_file, "r", encoding="utf-8") as f:
                    src_data = json.load(f)
                with open(dst_file, "r", encoding="utf-8") as f:
                    dst_data = json.load(f)
                    
                merged = merge_json(dst_data, src_data)
                
                with open(dst_file, "w", encoding="utf-8") as f:
                    json.dump(merged, f, indent=4)
                print("Apvienošana veiksmīga!")
            except Exception as e:
                print(f"Kļūda: {str(e)}")

        elif choice == "3":
            files = list_json_files()
            if not files:
                print("Nav failu!")
                continue
                
            print("\nPieejamie faili:")
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
                
            try:
                del_idx = int(input("Izvēlies dzēšamo failu (nr): ")) - 1
                target = files[del_idx]
                if input(f"Dzēst {target}? (jā/nē): ").lower() == "jā":
                    os.remove(target)
                    print("Fails dzēsts!")
            except Exception as e:
                print(f"Kļūda: {str(e)}")

        elif choice == "4":
            break

        else:
            print("Nepareiza izvēle!")

def main():
    parser = argparse.ArgumentParser(
        description="JSON apstrādes rīks ar drošu pārrakstīšanu un apvienošanu",
        epilog="Piemērs: ./script.py -c overwrite -f modem.json -o config.json"
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Interaktīvais režīms")
    parser.add_argument("-c", "--operation", choices=["merge", "overwrite"], help="Darbība: merge vai overwrite")
    parser.add_argument("-f", "--input", help="Ievades fails")
    parser.add_argument("-o", "--output", help="Izvades fails")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif all([args.operation, args.input, args.output]):
        process_command_line(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()


# 