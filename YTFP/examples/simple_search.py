"""
Yahoo!路線情報ライブラリの基本的な使用例

このスクリプトでは、指定した出発駅と到着駅の間の経路を検索し、結果を表示します。
"""

import json
import sys
import os

# ライブラリをインポートするためのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from yahoosc import YahooTransitAPI

def main():
    from_station = "服部天神"
    to_station = "新大阪"
    
    # Yahoo!路線情報クライアントを初期化
    with YahooTransitAPI() as api:
        # 駅名の候補を取得（オプション）
        print(f"「{from_station}」の候補を検索中...")
        from_suggestions = api.get_station_suggestions(from_station)
        print(json.dumps(from_suggestions, indent=2, ensure_ascii=False))
        
        print(f"「{to_station}」の候補を検索中...")
        to_suggestions = api.get_station_suggestions(to_station)
        print(json.dumps(to_suggestions, indent=2, ensure_ascii=False))
        
        # 経路検索の実行
        print(f"{from_station}から{to_station}への経路を検索中...")
        routes = api.search_routes(from_station, to_station)
        
        # 検索結果の表示
        if routes:
            print(f"抽出されたルート数: {len(routes)}")
            
            for i, route in enumerate(routes):
                print(f"\n--- {route.get('route_id', f'ルート {i+1}')} ---")
                print(f"  優先度: {route.get('priority')}")
                print(f"  出発時刻: {route.get('departure_time')}")
                print(f"  到着時刻: {route.get('arrival_time')}")
                print(f"  所要時間: {route.get('total_time')}")
                print(f"  乗車時間: {route.get('time_on_board')}")
                print(f"  乗換回数: {route.get('transfers')}")
                print(f"  料金: {route.get('fare')} ({route.get('fare_type', 'N/A')})")
                print(f"  距離: {route.get('distance')}")
                print(f"  詳細:")
                
                if route.get('details'):
                    for detail_item in route['details']:
                        if detail_item.get('type') == 'departure_station':
                            print(f"    出発駅: {detail_item.get('station_name')} ({detail_item.get('time')})")
                        elif detail_item.get('type') == 'arrival_station':
                            print(f"    到着駅: {detail_item.get('station_name')} ({detail_item.get('time')})")
                        elif detail_item.get('type') == 'transport':
                            print(f"    交通手段:")
                            print(f"      路線名: {detail_item.get('line_name')}")
                            print(f"      行先: {detail_item.get('destination')}{' (当駅始発)' if detail_item.get('is_first_train') else ''}")
                            print(f"      出発番線: {detail_item.get('departure_platform')}")
                            print(f"      到着番線: {detail_item.get('arrival_platform')}")
                            if detail_item.get('fare_segment'):
                                print(f"      区間料金: {detail_item.get('fare_segment')}")
                else:
                    print("    詳細情報なし")
            
            # 特定のルート (例: ルート1) のみJSON形式で表示
            if len(routes) > 0:
                print("\n--- ルート1 の詳細 (JSON形式) ---")
                print(json.dumps(routes[0], indent=2, ensure_ascii=False))
        else:
            print("ルート情報を抽出できませんでした。")

if __name__ == "__main__":
    main()