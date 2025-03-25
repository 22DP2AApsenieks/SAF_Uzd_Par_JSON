#!/usr/bin/env python3
import argparse
import json
import os
import sys

def merge_json(a, b):
    """
    Rekursīvi apvieno divus JSON objektus/dictionaries vai arrays.
    Ja diviem dictionaries atbilst vienādi atslēgas, tiek veikta rekursīva apvienošana.
    Ja divām arrays ir kopīgas vērtības, tās netiek dubļotas.
    Ja datu tipi neatbilst, otrā vērtība pārraksta pirmo.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        result = a.copy()
        for key, value in b.items():
            if key in result:
                result[key] = merge_json(result[key], value)
            else:
                result[key] = value
        return result
    elif isinstance(a, list) and isinstance(b, list):
        result = a.copy()
        for item in b:
            if item not in result:
                result.append(item)
        return result
    else:
        # Ja tipi nesakrīt, izmanto jauno vērtību (overwrite)
        return b

def process_command_line(args):
    """Apstrad.  merge vai overwrite."""
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data_input = json.load(f)
    except Exception as e:
        print("Kļūda ielādējot ievades failu:", e)
        sys.exit(1)
        
    if args.operation.lower() == "merge":
        # Ja izvades fails eksistē, ielādē esošo saturu, citādi sāk ar tukšu objektu.
        if os.path.exists(args.output):
            try:
                with open(args.output, "r", encoding="utf-8") as f:
                    data_output = json.load(f)
            except Exception as e:
                print("Kļūda ielādējot izvades failu:", e)
                data_output = {}
        else:
            data_output = {}
        merged = merge_json(data_output, data_input)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=4, ensure_ascii=False)
        print("Apvienotā informācija saglabāta failā", args.output)
        
    elif args.operation.lower() == "overwrite":
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data_input, f, indent=4, ensure_ascii=False)
        print("Ievades fails pārrakstīts uz", args.output)
    else:
        print("Neatpazīta operācija. Lūdzu, izmanto 'merge' vai 'overwrite'.")
        sys.exit(1)

def list_json_files():
    """Atrod un izvada sarakstu ar pašreizējā direktorijā esošajiem .json failiem."""
    files = [f for f in os.listdir(".") if f.endswith(".json")]
    if files:
        print("Pieejamie json faili:")
        for i, f in enumerate(files):
            print(f"  {i+1}. {f}")
    else:
        print("Nav pieejamu json failu.")
    return files

def interactive_mode():
    """Interaktīvais režīms, kur lietotājam tiek piedāvātas opcijas darbībām ar JSON failiem."""
    while True:
        print("\nIzvēlies opciju:")
        print("  1. Izveidot json")
        print("  2. Apvienot (merge json)")
        print("  3. Izdzēst json")
        print("  4. Izbeigt interaktīvo režīmu")
        choice = input("Tavs izvēle: ").strip()
        
        if choice == "1":
            list_json_files()
            filename = input("Ievadi jauna json faila nosaukumu (piem., new.json): ").strip()
            content = input("Ievadi json saturu (piem., {} vai derīgu json tekstu): ").strip()
            try:
                data = json.loads(content)
            except Exception as e:
                print("Nederīgs json saturs. Kļūda:", e)
                continue
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print("Fails", filename, "izveidots.")
            except Exception as e:
                print("Kļūda saglabājot failu:", e)
                
        elif choice == "2":
            files = list_json_files()
            if len(files) < 2:
                print("Nepietiekama json failu skaits merge operācijai (vajag vismaz 2 failus).")
                continue
            base_file = input("Ievadi bāzes faila nosaukumu (kurš tiks papildināts): ").strip()
            merge_file = input("Ievadi faila nosaukumu, kuru apvienot ar bāzes failu: ").strip()
            try:
                with open(base_file, "r", encoding="utf-8") as f:
                    data_base = json.load(f)
                with open(merge_file, "r", encoding="utf-8") as f:
                    data_merge = json.load(f)
            except Exception as e:
                print("Kļūda ielādējot failus:", e)
                continue
            merged = merge_json(data_base, data_merge)
            output_file = input("Ievadi jauna faila nosaukumu, kur saglabāt rezultātu: ").strip()
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(merged, f, indent=4, ensure_ascii=False)
                print("Merge operācija veiksmīgi pabeigta, rezultāts saglabāts failā", output_file)
            except Exception as e:
                print("Kļūda saglabājot failu:", e)
                
        elif choice == "3":
            files = list_json_files()
            file_to_delete = input("Ievadi dzēšamā json faila nosaukumu: ").strip()
            if os.path.exists(file_to_delete):
                try:
                    os.remove(file_to_delete)
                    print("Fails", file_to_delete, "dzēsts.")
                except Exception as e:
                    print("Kļūda dzēšot failu:", e)
            else:
                print("Fails netika atrasts.")
                
        elif choice == "4":
            print("Izbeigt interaktīvo režīmu.")
            break
        else:
            print("Nederīga izvēle. Lūdzu, mēģini vēlreiz.")

def main():
    parser = argparse.ArgumentParser(
        description="Primitīva JSON operāciju programma (merge/overwrite) ar interaktīvo režīmu."
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Palaist programmu interaktīvā režīmā")
    parser.add_argument("-c", "--operation", type=str, help="Operācija: merge vai overwrite")
    parser.add_argument("-f", "--input", type=str, help="Ievades faila nosaukums")
    parser.add_argument("-o", "--output", type=str, help="Izvades faila nosaukums")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.operation and args.input and args.output:
        process_command_line(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
