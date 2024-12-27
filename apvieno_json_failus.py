import json
import os

def merge_json_files(file_names, output_file, conflict_resolution='overwrite'):
    

    merged_data = []

    for file_name in file_names:
        if not os.path.exists(file_name):
            print(f"Brīdinājums: fails '{file_name}' neeksistē!") #izvada, kurš fails nav atrasts(ja neatrada)
            continue

        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f) #lade datus no faila(es tā sapratu)
        except json.JSONDecodeError as e:
            print(f"Kļūda atverot failu {file_name}: {e}")
            continue

        for new_object in data:
            # Pārbaudām, vai nosaukums jau pastav
            existing_object = next((obj for obj in merged_data if obj.get('name') == new_object.get('name')), None)

            if existing_object:
                if conflict_resolution == 'overwrite':
                    # Paraksta, aizstajot veco ar jauno
                    merged_data.remove(existing_object)
                    merged_data.append(new_object)
                elif conflict_resolution == 'merge':
                    # Apvienot
                    existing_object.update(new_object)
                elif conflict_resolution == 'skip':
                    # Ignorēt jauno 
                    continue
            else:
                # Ja neeksistē, pievienot
                merged_data.append(new_object)

    # Saglabā rezultātu failā
    try:
        with open(output_file, 'w', encoding='utf-8') as output:
            json.dump(merged_data, output, indent=4, ensure_ascii=False)
        print(f"Summētais fails ir saglabāts kā '{output_file}'")
    except Exception as e:
        print(f"Kļūda saglabājot rezultātu: {e}")


#šeit varat darboties, var izdzest kadu failu, ja nepieciesams un atkal pavienot(stradas). Daudzoko var parbaudit, bet tiesi nakamaja koda rinda ir faili ar kuriem darbibas notiks. Vēlams neivadit "saf_..." failu, jo tad nesaglabasies un bus kluda, jo sintakse šiem(apvienosanas) json failiem ir savadaka, kā valiacijas([] pret {})
file_names = ['programmesanasval.json', 'masinas.json', 'saf_darbinieki.json']
output_file = 'merged_output.json'

merge_json_files(file_names, output_file, conflict_resolution='merge')
