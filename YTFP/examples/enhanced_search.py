"""
拡張API（キャッシング対応）の使用例

このサンプルは、キャッシング機能を持ったEnhancedYahooTransitAPIの使い方を示します。
"""

import sys
import os
import json
import time

# ライブラリのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from yahoosc import EnhancedYahooTransitAPI, logger

def main():
    from_station = "服部天神"
    to_station = "新大阪"
    
    # カスタムキャッシュ設定を指定
    cache_config = {
        "ttl": 300,  # 5分間キャッシュを保持
        "use_file_cache": True,  # ファイルキャッシュを使用
        "max_memory_entries": 50  # メモリキャッシュに最大50エントリを保持
    }
    
    # キャッシング対応APIクライアントを初期化
    with EnhancedYahooTransitAPI(cache_config=cache_config) as api:
        # 1回目のリクエスト（キャッシュなし）
        print("===== 1回目のリクエスト（APIから取得）=====")
        start_time = time.time()
        
        print(f"「{from_station}」の候補を検索中...")
        from_suggestions = api.get_station_suggestions(from_station)
        
        print(f"「{to_station}」の候補を検索中...")
        to_suggestions = api.get_station_suggestions(to_station)
        
        print(f"{from_station}から{to_station}への経路を検索中...")
        routes = api.search_routes(from_station, to_station)
        
        first_request_time = time.time() - start_time
        print(f"所要時間: {first_request_time:.2f}秒")
        
        if routes:
            print(f"抽出されたルート数: {len(routes)}")
            print(f"最初のルート: {routes[0].get('route_id', 'ルート1')}")
        
        # 2回目のリクエスト（キャッシュから取得）
        print("\n===== 2回目のリクエスト（キャッシュから取得）=====")
        start_time = time.time()
        
        print(f"「{from_station}」の候補を再度検索中...")
        from_suggestions = api.get_station_suggestions(from_station)
        
        print(f"「{to_station}」の候補を再度検索中...")
        to_suggestions = api.get_station_suggestions(to_station)
        
        print(f"{from_station}から{to_station}への経路を再度検索中...")
        routes = api.search_routes(from_station, to_station)
        
        second_request_time = time.time() - start_time
        print(f"所要時間: {second_request_time:.2f}秒")
        
        if routes:
            print(f"抽出されたルート数: {len(routes)}")
            print(f"最初のルート: {routes[0].get('route_id', 'ルート1')}")
        
        # 速度比較
        print("\n===== パフォーマンス比較 =====")
        speedup = first_request_time / second_request_time if second_request_time > 0 else float('inf')
        print(f"1回目（APIから取得）: {first_request_time:.2f}秒")
        print(f"2回目（キャッシュから取得）: {second_request_time:.2f}秒")
        print(f"高速化率: {speedup:.1f}倍")

if __name__ == "__main__":
    main()