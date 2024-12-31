import json
import os
import unittest

def merge_json_files(file_names, output_file, conflict_resolution='overwrite'):
    merged_data = [] #kur/kādā formatā dati tiks ievadīti iekšā

    for file_name in file_names:
        if not os.path.exists(file_name):
            print(f"Brīdinājums: fails '{file_name}' neeksistē!")  #uzrei pabridina, ja failu nevar atrast
            continue

        try:
            with open(file_name, 'r', encoding='utf-8') as f: #r = faila lasīšanas režīms // lai nodrošinātu pareizu teksta apstrādi
                data = json.load(f)  #Lade json datus no faila/iem(cik es sapratu)
        except json.JSONDecodeError as e:
            print(f"Kļūda atverot failu {file_name}: {e}") #nevar atvert failu
            continue

        for new_object in data:
            existing_object = next((obj for obj in merged_data if obj.get('name') == new_object.get('name')), None) #parbauda, vai objekts eksiste

            if existing_object:
                if conflict_resolution == 'overwrite':  #overwrite = tiks veikta pārrakstīšana(datu)
                    merged_data.remove(existing_object) #noņesms veco datus
                    merged_data.append(new_object) #atjaunos ar jaunajiem
                elif conflict_resolution == 'merge': #japapildina
                    existing_object.update(new_object)
                elif conflict_resolution == 'skip': #izlaiž darbību, nepārrakstot esošo objektu
                    continue
            else:
                merged_data.append(new_object) # ja nekas no iepreikšējajām izvēlēm nenotiks, tad programma vnk tpt pievienos datus

    try:
        with open(output_file, 'w', encoding='utf-8') as output:
            json.dump(merged_data, output, indent=4, ensure_ascii=False) # Ieraksta datus JSON formātā (ar 4 atstarpem)
        print(f"Summētais fails ir saglabāts kā '{output_file}'")
    except Exception as e: #izņēmums(error)
        print(f"Kļūda saglabājot rezultātu: {e}")


def create_example_files(): #šeit es izveidoju piemēra json failu(kur ir 3 dažādi faili)
    example_files = {
        'programmesanasval.json': [
            {"name": "Python", "value": "Popular"},
            {"name": "Java", "value": "Widely Used"}
        ],
        'masinas.json': [
            {"name": "Tesla", "value": "Electric"},
            {"name": "Toyota", "value": "Hybrid"}
        ],
        'saf_darbinieki2.json': [
            {"name": "John Doe", "value": "Manager"},
            {"name": "Jane Smith", "value": "Engineer"}
        ]
    }

    for file_name, content in example_files.items():
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4, ensure_ascii=False)  #Ieraksta datus failā (f) ar 4 atstarpēm


class TestMergeJsonFiles(unittest.TestCase): # testa clase

    def setUp(self):
        create_example_files() #izveido piemēra failus

    def test_merge_json_files(self):
        file_names = ['programmesanasval.json', 'masinas.json', 'saf_darbinieki2.json'] #faili, kurus apvieo
        output_file = 'merged_output_testam.json' #gala rezultats(apvienotie faili vienā)

        merge_json_files(file_names, output_file, conflict_resolution='merge') #Izsauc funkc (merge_json_files), lai apvienotu failus 

        # parbauda vai "output" fails eksistē
        self.assertTrue(os.path.exists(output_file), f"Fails '{output_file}' neeksistē")

        with open(output_file, 'r', encoding='utf-8') as f: #lai nolasītu tā saturu(lasisanas rezims = 'r')
            merged_data = json.load(f) #cik es sparat, pārbauda datu strukturu

        # Pārbaudes
        self.assertEqual(len(merged_data), 6, f"Nepareizs apvienotā datu skaits ({len(merged_data)})")
        self.assertTrue(any(item.get('name') == 'Python' for item in merged_data), "'Python' nav apvienotajos datos") #ja neviens šāds objekts netiek atrasts, tad izmetis error
        self.assertTrue(any(item.get('name') == 'Tesla' for item in merged_data), "'Tesla' nav apvienotajos datos")
        self.assertTrue(any(item.get('name') == 'John Doe' for item in merged_data), "'John Doe' nav apvienotajos datos")


if __name__ == '__main__': #vairak paredzet lai palaistu unittest beigās
    unittest.main() #izpilda unittest
