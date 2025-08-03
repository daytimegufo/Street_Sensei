
import json
import requests
import time
import os

def geocode_address(address, country="日本"):
    query = f"東京都 {address}"
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 0,
        "limit": 1,
        "country": country
    }
    headers = {
        "User-Agent": "GeoTextbookGeocoder/1.0 (nbasic296@gmail.com)"  # 実在のメールに変更推奨
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"❌ Geocoding failed: {address} → {e}")
    return None, None

def enrich_missing_coords(coords_file, locations_file, output_file):
    with open(coords_file, "r", encoding="utf-8") as f:
        facilities = json.load(f)
    with open(locations_file, "r", encoding="utf-8") as f:
        location_data = json.load(f)

    name_to_address = {entry["name"]: entry.get("address") for entry in location_data}
    final_facilities = []

    for fac in facilities:
        if fac.get("lat") is not None and fac.get("lng") is not None:
            final_facilities.append(fac)
            continue

        name = fac.get("name")
        address = name_to_address.get(name)
        if address:
            lat, lng = geocode_address(address)
            if lat and lng:
                fac["lat"] = lat
                fac["lng"] = lng
                print(f"📍 Added: {name} ({address}) → {lat}, {lng}")
            else:
                print(f"⚠️ Skipped: {name} (no result)")
        else:
            print(f"⚠️ No address found for: {name}")
        final_facilities.append(fac)
        time.sleep(1.5)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_facilities, f, ensure_ascii=False, indent=2)
    print(f"✅ Output saved to: {output_file}")

# ▼ ファイル名（必要に応じて変更）
if __name__ == "__main__":
    coords_file = "東京23区武三-with-coords.json"
    locations_file = "C:/Street_Sensei/locations.json"
    output_file = "東京23区武三-with-geo.json"
    enrich_missing_coords(coords_file, locations_file, output_file)