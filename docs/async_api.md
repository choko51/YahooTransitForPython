# 非同期API (asyncio)

Yahoo!路線情報ライブラリの非同期API機能について説明します。

## 概要

非同期API機能は、Python標準ライブラリの`asyncio`と`aiohttp`を活用して、I/O待ち時間を効率的に活用する非同期処理を実現します。これにより、特に複数のリクエストを並行して行う場合や、他の非同期処理と組み合わせる場合に高いパフォーマンスを発揮します。

非同期APIには以下の2つのクラスが用意されています：
- **AsyncYahooTransitAPI** - 基本的な非同期API機能
- **AsyncEnhancedYahooTransitAPI** - キャッシング機能を備えた非同期API

## 基本的な使い方

### AsyncYahooTransitAPIの使用

非同期APIを使用するには、`AsyncYahooTransitAPI`クラスを使用し、非同期コンテキストマネージャとして操作します：

```python
import asyncio
from yahoosc import AsyncYahooTransitAPI

async def main():
    # 非同期コンテキストマネージャーとして使用
    async with AsyncYahooTransitAPI() as api:
        # 駅名候補を非同期に取得
        suggestions = await api.get_station_suggestions_async("新宿")
        print(suggestions)
        
        # 経路検索を非同期に実行
        routes = await api.search_routes_async("服部天神", "新大阪")
        print(f"ルート数: {len(routes)}")

# 非同期関数の実行
asyncio.run(main())
```

### 並行リクエストの実行

非同期APIの大きな利点は、複数のリクエストを並行して実行できることです：

```python
import asyncio
from yahoosc import AsyncYahooTransitAPI

async def main():
    async with AsyncYahooTransitAPI() as api:
        # 複数の駅名候補を並行して取得
        tokyo_task = api.get_station_suggestions_async("東京")
        kyoto_task = api.get_station_suggestions_async("京都")
        osaka_task = api.get_station_suggestions_async("大阪")
        
        # 全てのタスクが完了するまで待機
        tokyo_result, kyoto_result, osaka_result = await asyncio.gather(
            tokyo_task, kyoto_task, osaka_task
        )
        
        # 各結果の処理
        print(f"東京の候補: {len(tokyo_result.get('Result', []))}件")
        print(f"京都の候補: {len(kyoto_result.get('Result', []))}件")
        print(f"大阪の候補: {len(osaka_result.get('Result', []))}件")

asyncio.run(main())
```

### 複数の経路検索の並行実行

複数の出発地-目的地ペアの経路検索を並行して実行するサンプル：

```python
import asyncio
from yahoosc import AsyncYahooTransitAPI

async def main():
    # 複数の出発地-目的地ペア
    routes_to_search = [
        ("服部天神", "新大阪"),
        ("大阪", "京都"),
        ("難波", "三宮"),
    ]
    
    async with AsyncYahooTransitAPI() as api:
        # 並行してすべての経路検索タスクを作成
        tasks = [
            api.search_routes_async(from_station, to_station)
            for from_station, to_station in routes_to_search
        ]
        
        # すべてのタスクが完了するまで待機
        results = await asyncio.gather(*tasks)
        
        # 結果の処理
        for (from_station, to_station), routes in zip(routes_to_search, results):
            print(f"{from_station}→{to_station}: {len(routes)}件のルート")
            if routes:
                print(f"  最初のルート: {routes[0].get('route_id', 'ルート1')}")

asyncio.run(main())
```

## キャッシング対応の非同期API

キャッシング機能と非同期処理を組み合わせることで、さらなるパフォーマンス向上が期待できます：

```python
import asyncio
from yahoosc import AsyncEnhancedYahooTransitAPI

async def main():
    # キャッシング設定
    cache_config = {
        "ttl": 1800,  # 30分間キャッシュを保持
        "use_file_cache": True
    }
    
    async with AsyncEnhancedYahooTransitAPI(cache_config=cache_config) as api:
        # 1回目のリクエスト（APIから取得）
        routes = await api.search_routes_async("服部天神", "新大阪")
        
        # 2回目のリクエスト（キャッシュから取得）
        routes_cached = await api.search_routes_async("服部天神", "新大阪")
        
        # 並行リクエストも可能
        tokyo_kyoto = api.search_routes_async("東京", "京都")
        osaka_kobe = api.search_routes_async("大阪", "神戸")
        
        # 両方のリクエスト結果を待機
        route1, route2 = await asyncio.gather(tokyo_kyoto, osaka_kobe)

asyncio.run(main())
```

## 詳細設定

### カスタムセッションの使用

既存の`aiohttp.ClientSession`を使用する場合は、コンストラクタに渡すことができます：

```python
import aiohttp
import asyncio
from yahoosc import AsyncYahooTransitAPI

async def main():
    # カスタムヘッダーやオプションを持つセッションを作成
    session = aiohttp.ClientSession(
        headers={"User-Agent": "MyCustomUserAgent"},
        timeout=aiohttp.ClientTimeout(total=30)
    )
    
    try:
        # 作成したセッションを使用
        async with AsyncYahooTransitAPI(session=session) as api:
            routes = await api.search_routes_async("服部天神", "新大阪")
            print(f"ルート数: {len(routes)}")
    finally:
        # セッションのクローズは自分で行う必要がある
        await session.close()

asyncio.run(main())
```

### カスタムヘッダーの設定

リクエストヘッダーをカスタマイズする場合：

```python
custom_headers = {
    "User-Agent": "MyCustomUserAgent",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

async with AsyncYahooTransitAPI(headers=custom_headers) as api:
    # APIリクエストにはカスタムヘッダーが使用される
    routes = await api.search_routes_async("服部天神", "新大阪")
```

## エラーハンドリング

非同期APIでのエラーハンドリングは、標準のPythonの例外処理と同様に行うことができます：

```python
import asyncio
from yahoosc import AsyncYahooTransitAPI, RequestError, ParseError

async def main():
    try:
        async with AsyncYahooTransitAPI() as api:
            routes = await api.search_routes_async("存在しない駅名", "新大阪")
    except RequestError as e:
        print(f"HTTPリクエストエラー: {e.status_code} - {e.message}")
    except ParseError as e:
        print(f"HTML解析エラー: {e.message}")
    except Exception as e:
        print(f"その他のエラー: {str(e)}")

asyncio.run(main())
```

## 内部の仕組み

### 非同期処理の流れ

1. `aiohttp.ClientSession`を使用して非同期HTTPリクエストを送信
2. レスポンスを非同期に受信
3. 受信したHTMLを（現在は同期的に）解析
4. 解析結果を返却

### セッション管理

`AsyncYahooTransitAPI`クラスは内部で`aiohttp.ClientSession`を管理します：

1. コンストラクタでセッションが指定されない場合、内部で新しいセッションを作成
2. `__aenter__`で非同期コンテキストマネージャーとして使用可能
3. `__aexit__`で内部作成されたセッションを自動的にクローズ

### 非同期パーサーについて

現在のバージョンでは、HTML解析処理（`extract_routes_from_html`）は同期的に行われています。これは、HTMLパース処理が主にCPUバウンドな処理であり、非同期化による大きなメリットが期待できないためです。将来のバージョンでは、特定のユースケースに応じて非同期パーサーが実装される可能性があります。

## パフォーマンスの考慮事項

- 単一のリクエストでは、非同期APIと同期APIの間に大きなパフォーマンス差はありません
- 複数のリクエストを並行して行う場合、非同期APIは大幅なパフォーマンス向上をもたらします
- 非同期APIは他の非同期処理（例：Webサーバー、GUI処理など）と組み合わせる場合に特に有用です
- 大量の並行リクエストを行う場合、対象サーバーへの負荷を考慮してレート制限を設けることをお勧めします