import json
import requests
import time

def search_wikidata(name, lang='ja'):
    url = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbsearchentities',
        'search': name,
        'language': lang,
        'format': 'json',
        'type': 'item'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('search'):
            return data['search'][0].get('id'), data['search'][0].get('label'), data['search'][0].get('description')
    except Exception as e:
        print(f"Error searching '{name}': {e}")
    return None, None, None

def enrich_with_wikidata(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        facilities = json.load(f)

    enriched = []
    for fac in facilities:
        name = fac.get('name')
        qid, label, desc = search_wikidata(name)
        fac['wikidata'] = qid
        fac['wikidata_label'] = label
        fac['wikidata_description'] = desc
        print(f"🔎 {name} → {qid or 'なし'}")
        time.sleep(1.2)
        enriched.append(fac)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

# ✅ これがないと python enrich_wikidata.py では何も起きません
if __name__ == "__main__":
    enrich_with_wikidata("東京23区武三.json", "東京23区武三-with-wikidata.json")
