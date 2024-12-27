import json

def validate_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  
            json.loads(content)  # Cik es sapratu, meģina paņemt kā JSON
        return "Pareizs!"  # Ja json fail ir pareizs
    except json.JSONDecodeError as e:
        return f"Kļūda JSON sintaksē: {e.msg} (pozīcija: rinda {e.lineno}, kolonna {e.colno})" # atrod kļūdu b parāda, kur tā sākas
    except FileNotFoundError:
        return "Fails netika atrasts. Lūdzu, pārbaudiet faila ceļu." # failu neatrada
    except Exception as e:
        return f"Nezināma kļūda: {str(e)}" # kkas nav pareizi ar failu vai programmu

# Tests
if __name__ == "__main__":
    file_path = "saf_darbinieki.json"  # Norādi pārbaudāmo failu, vainu "saf_darbinieki.json"(atbildei jabut: pareizi) vs "saf_darbinieki.json"(atbildei jabut: kļūda)
    result = validate_json_file(file_path)
    print(result)
