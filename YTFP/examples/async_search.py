"""
非同期API（asyncio対応）の使用例

このサンプルは、AsyncYahooTransitAPIとAsyncEnhancedYahooTransitAPIの使い方を示します。
"""

import sys
import os
import json
import time
import asyncio
from typing import List, Dict, Any

# ライブラリのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from yahoosc import AsyncYahooTransitAPI, AsyncEnhancedYahooTransitAPI, logger

async def basic_search():
    """基本的な非同期検索の例"""
    from_station = "服部天神"
    to_station = "新大阪"
    
    # 非同期APIクライアントを初期化
    async with AsyncYahooTransitAPI() as api:
        print("===== 基本的な非同期検索 =====")
        
        # 並行してリクエストを実行
        start_time = time.time()
        
        print(f"「{from_station}」と「{to_station}」の候補を並行検索中...")
        # 並行して両方の駅名候補を取得
        from_task = asyncio.create_task(api.get_station_suggestions_async(from_station))
        to_task = asyncio.create_task(api.get_station_suggestions_async(to_station))
        
        # 両方の完了を待機
        from_suggestions, to_suggestions = await asyncio.gather(from_task, to_task)
        
        print(f"「{from_station}」の候補: {len(from_suggestions.get('Result', []))}件")
        print(f"「{to_station}」の候補: {len(to_suggestions.get('Result', []))}件")
        
        # 経路検索
        print(f"{from_station}から{to_station}への経路を検索中...")
        routes = await api.search_routes_async(from_station, to_station)
        
        elapsed_time = time.time() - start_time
        print(f"所要時間: {elapsed_time:.2f}秒")
        
        if routes:
            print(f"抽出されたルート数: {len(routes)}")
            print(f"最初のルート: {routes[0].get('route_id', 'ルート1')}")

async def enhanced_search():
    """キャッシング対応の非同期検索の例"""
    from_station = "服部天神"
    to_station = "新大阪"
    
    # カスタムキャッシュ設定
    cache_config = {
        "ttl": 300,  # 5分間キャッシュを保持
        "use_file_cache": True
    }
    
    # 拡張非同期APIクライアントを初期化
    async with AsyncEnhancedYahooTransitAPI(cache_config=cache_config) as api:
        # 1回目のリクエスト（キャッシュなし）
        print("\n===== 1回目の非同期リクエスト（APIから取得）=====")
        start_time = time.time()
        
        # 並行して駅名候補と経路を取得
        from_task = asyncio.create_task(api.get_station_suggestions_async(from_station))
        to_task = asyncio.create_task(api.get_station_suggestions_async(to_station))
        routes_task = asyncio.create_task(api.search_routes_async(from_station, to_station))
        
        # 全てのタスクの完了を待機
        from_suggestions, to_suggestions, routes = await asyncio.gather(
            from_task, to_task, routes_task
        )
        
        first_request_time = time.time() - start_time
        print(f"所要時間: {first_request_time:.2f}秒")
        
        if routes:
            print(f"抽出されたルート数: {len(routes)}")
        
        # 2回目のリクエスト（キャッシュから取得）
        print("\n===== 2回目の非同期リクエスト（キャッシュから取得）=====")
        start_time = time.time()
        
        # 並行して駅名候補と経路を取得
        from_task = asyncio.create_task(api.get_station_suggestions_async(from_station))
        to_task = asyncio.create_task(api.get_station_suggestions_async(to_station))
        routes_task = asyncio.create_task(api.search_routes_async(from_station, to_station))
        
        # 全てのタスクの完了を待機
        from_suggestions, to_suggestions, routes = await asyncio.gather(
            from_task, to_task, routes_task
        )
        
        second_request_time = time.time() - start_time
        print(f"所要時間: {second_request_time:.2f}秒")
        
        if routes:
            print(f"抽出されたルート数: {len(routes)}")
        
        # 速度比較
        print("\n===== パフォーマンス比較 =====")
        speedup = first_request_time / second_request_time if second_request_time > 0 else float('inf')
        print(f"1回目（APIから取得）: {first_request_time:.2f}秒")
        print(f"2回目（キャッシュから取得）: {second_request_time:.2f}秒")
        print(f"高速化率: {speedup:.1f}倍")

async def multi_route_search():
    """複数経路の並行検索例"""
    # 複数の出発地-目的地ペア
    station_pairs = [
        ("服部天神", "新大阪"),
        ("大阪", "京都"),
        ("難波", "三宮"),
    ]
    
    print("\n===== 複数経路の並行検索 =====")
    start_time = time.time()
    
    # 拡張非同期APIクライアントを初期化
    async with AsyncEnhancedYahooTransitAPI() as api:
        # 並行して複数の経路検索タスクを作成
        tasks = []
        for from_station, to_station in station_pairs:
            task = asyncio.create_task(api.search_routes_async(from_station, to_station))
            tasks.append((from_station, to_station, task))
        
        # 全てのタスクの結果を収集
        for from_station, to_station, task in tasks:
            routes = await task
            print(f"{from_station}→{to_station}: {len(routes)}件のルートを取得")
            if routes:
                print(f"  最初のルート: {routes[0].get('route_id', 'ルート1')}")
                print(f"  所要時間: {routes[0].get('total_time', 'N/A')}")
    
    elapsed_time = time.time() - start_time
    print(f"合計所要時間: {elapsed_time:.2f}秒")

async def main():
    """メイン関数"""
    # 基本的な非同期検索
    await basic_search()
    
    # キャッシング対応の非同期検索
    await enhanced_search()
    
    # 複数経路の並行検索
    await multi_route_search()

if __name__ == "__main__":
    asyncio.run(main())