import json
import requests
import time

def fetch_coords_from_qid(qid):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        entity = data["entities"].get(qid)
        if not entity:
            return None, None
        claims = entity.get("claims", {})
        if "P625" in claims:
            coord_data = claims["P625"][0]["mainsnak"]["datavalue"]["value"]
            return coord_data["latitude"], coord_data["longitude"]
    except Exception as e:
        print(f"Error fetching coordinates for {qid}: {e}")
    return None, None

def enrich_coords_with_wikidata(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        facilities = json.load(f)

    for fac in facilities:
        if fac.get("wikidata") and (not fac.get("lat") or not fac.get("lng")):
            lat, lng = fetch_coords_from_qid(fac["wikidata"])
            if lat and lng:
                fac["lat"] = lat
                fac["lng"] = lng
                print(f"📍 補完: {fac['name']} → {lat}, {lng}")
            time.sleep(1.2)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(facilities, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    enrich_coords_with_wikidata("東京23区武三-with-wikidata.json", "東京23区武三-with-coords.json")
