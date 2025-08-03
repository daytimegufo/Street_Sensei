
import json
import requests
import time

# 🔐 ここにあなたのAPIキーを記入
GOOGLE_API_KEY = "AIzaSyC2W9TDlRAuqt_qOK_06t-CWOmxsEIzJCA"

def geocode_address_google(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": f"東京都 {address}",
        "key": GOOGLE_API_KEY,
        "language": "ja"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK" and data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            print(f"⚠️ No result for: {address} → {data['status']}")
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
            lat, lng = geocode_address_google(address)
            if lat and lng:
                fac["lat"] = lat
                fac["lng"] = lng
                print(f"📍 Added: {name} ({address}) → {lat}, {lng}")
            else:
                print(f"⚠️ Skipped: {name} (no result)")
        else:
            print(f"⚠️ No address found for: {name}")
        final_facilities.append(fac)
        time.sleep(0.5)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_facilities, f, ensure_ascii=False, indent=2)
    print(f"✅ Output saved to: {output_file}")

if __name__ == "__main__":
    coords_file = "東京23区武三-with-coords.json"
    locations_file = "C:/Street_Sensei/locations.json"
    output_file = "東京23区武三-with-geo.json"
    enrich_missing_coords(coords_file, locations_file, output_file)