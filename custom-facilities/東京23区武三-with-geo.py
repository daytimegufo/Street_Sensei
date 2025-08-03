import json
import requests
import time

def geocode_address(address, country="日本"):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 0,
        "limit": 1,
        "country": country
    }
    headers = {
        "User-Agent": "GeoTextbookGeocoder/1.0 (your-email@example.com)"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"❌ Failed: {address} → {e}")
    return None, None

def enrich_with_geocoding(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        facilities = json.load(f)

    for fac in facilities:
        if not fac.get("lat") or not fac.get("lng"):
            address = fac.get("address") or fac.get("name")  # nameでも代用
            lat, lng = geocode_address(address)
            if lat and lng:
                fac["lat"] = lat
                fac["lng"] = lng
                print(f"📍 補完: {address} → {lat}, {lng}")
            time.sleep(1.2)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(facilities, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    enrich_with_geocoding("東京23区武三-with-wikidata.json", "東京23区武三-with-geo.json")
