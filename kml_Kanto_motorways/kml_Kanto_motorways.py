import geopandas as gpd
import os
from shapely.geometry import LineString
import simplekml
from zipfile import ZipFile

# 入力ファイル（GeoJSON形式）
geojson_path = r"C:\Street_Sensei\kml_Kanto_motorways\N06-20_HighwaySection.geojson"
output_dir = "kanto_highways_kml"
os.makedirs(output_dir, exist_ok=True)

# 関東高速道路名称の一部
target_keywords = [
    '首都', '中央自動車道', '東名', '関越', '常磐', '京葉道路', '第三京浜', '外環',
    '湾岸線', '東京湾アクアライン', '圏央道', '小田原厚木道路', '横浜新道', '横浜横須賀',
    '北関東自動車道', '新東名', '新湘南', '上信越', '館山自動車道', '千葉東金', '富津館山',
    'アネスト岩田', '西湘バイパス', '三浦縦貫', '逗葉新道', '東関東', '新空港', '日光宇都宮',
    '東北自動車道', '首都圏中央連絡', '東京外環', '神奈川', '晴海線'
]

# GeoDataFrameを読み込む
gdf = gpd.read_file(geojson_path)

# N06_007(ROAD_NAME)列があるか確認
if 'N06_007' not in gdf.columns:
    print("❌ 'N06_007' カラムが見つかりません。以下の列が利用可能です：")
    print(gdf.columns)
    exit()

# N06_007に関東高速のキーワードが含まれる行を抽出
gdf_kanto = gdf[gdf['N06_007'].fillna('').apply(lambda name: any(kw in name for kw in target_keywords))]

# 抽出結果の確認
print(f"✅ 関東高速道路数（重複含む）: {len(gdf_kanto)}")

# 道路名称ごとにグループ化
grouped = gdf_kanto.groupby('N06_007')

# KMLファイルを出力
for N06_007, group in grouped:
    if not N06_007:
        continue  # 空白名をスキップ
    kml = simplekml.Kml()
    for _, row in group.iterrows():
        if isinstance(row.geometry, LineString):
            coords = [(x, y) for x, y in row.geometry.coords]
            kml.newlinestring(name=N06_007, coords=coords)
    safe_name = N06_007.replace("/", "_").replace(" ", "_").replace("・", "_")
    kml.save(os.path.join(output_dir, f"{safe_name}.kml"))

# ZIP化
with ZipFile(output_dir + ".zip", 'w') as zipf:
    for root, _, files in os.walk(output_dir):
        for file in files:
            full_path = os.path.join(root, file)
            zipf.write(full_path, arcname=file)

print("✅ KMLファイルの出力とZIP圧縮が完了しました。")
