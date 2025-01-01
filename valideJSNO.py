import json
import os
import unittest  # vajadzig, lai varu veidot testu

def validate_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file: #r = read režīms // cik saprat, apstrada faila saturu
            content = file.read()
            json.loads(content)  #lade json
        return "Pareizs!"  #Ja faila formats ir pareizs
    except json.JSONDecodeError as e:
        return f"Kļūda JSON sintaksē: {e.msg} (pozīcija: rinda {e.lineno}, kolonna {e.colno})"  #Ja atrasta kāda(pirmā) kļūda failā
    except FileNotFoundError:
        return "Fails netika atrasts. Lūdzu, pārbaudiet faila ceļu."  #Ja neatrada failu
    except Exception as e:
        return f"Nezināma kļūda: {str(e)}"  #Kautkads cits iemesls

# Vajadzigs lai uzreiz testetu(cik es sapratu) // name piešķir main = prioritāti
if __name__ == "__main__":
    file_path = "saf_darbinieki_nep.json"  #Norādi pārbaudāmo failu, vainu "saf_darbinieki.json"(atbildei jabut: pareizi) vs "saf_darbinieki_nep.json"(atbildei jabut: "kļūda...")
    result = validate_json_file(file_path)
    print(result)

    #unitest šaja clase
    class TestValidateJsonFile(unittest.TestCase):

        def test_valid_json(self): #pareizais tests
            valid_file = 'test_valid.json'
            valid_data = [{"name": "item1", "value": 100}, {"name": "item2", "value": 200}] #100 un 200 ir vienkārši:"placeholders for numbers and have no specific meaning"
            with open(valid_file, 'w', encoding='utf-8') as f:
                json.dump(valid_data, f, indent=4) #f = fails(lkm) // Ieraksta 'valid_data' objektu 'f'

            result = validate_json_file(valid_file) #saglabā "result"
            self.assertEqual(result, "Pareizs!")
            os.remove(valid_file)

        def test_invalid_json(self): #nepareizais tests
            invalid_file = 'test_invalid.json'
            with open(invalid_file, 'w', encoding='utf-8') as f: #w = rakstisanas rezims
                f.write('{"name": "item1", "value": 100')  #simule nepareizu ievadi(trūkst beigās"}")
            result = validate_json_file(invalid_file)
            self.assertTrue(result.startswith("Kļūda JSON sintaksē:"))
            os.remove(invalid_file) #nonem(dzēš) pagaidu failu

        def test_file_not_found(self): #tests, kur netiek atrasts fails
            missing_file = 'non_existing_file.json'
            result = validate_json_file(missing_file) 
            self.assertEqual(result, "Fails netika atrasts. Lūdzu, pārbaudiet faila ceļu.")

        def test_unknown_error(self): #nezinama error tests
            from unittest.mock import patch #"Ar patch var aizstāt ārējos resursus, piemēram, failu sistēmu, tīkla pieprasījumus, datubāzi vai jebkuru citu ārēju pakalpojumu"
            with patch('builtins.open', side_effect=Exception("Unknown error")):
                result = validate_json_file('some_file.json') #funkc mēģina atvērt failu, kas izraisīs klūdu
                self.assertEqual(result, "Nezināma kļūda: Unknown error")

    # tikai koda beigas palaizam testu (testa metodes)
    unittest.main() 
