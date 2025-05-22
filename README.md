# Yahoo!路線情報スクレイピングライブラリ

このライブラリは、Yahoo!路線情報から経路情報を取得するための非公式APIクライアントです。
v0.2.0からキャッシング機能と非同期処理（asyncio）がサポートされました。

## 機能

- 駅名候補の取得
- 駅間の経路検索
- キャッシング機能
- 非同期API (asyncio)
- 拡張エラーハンドリング
- ロギング機能

## インストール方法

### ローカルインストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/yahoosc.git
cd yahoosc

# ライブラリをインストール
pip install -e .

# 開発用ツールも含めてインストール（テスト等）
pip install -e ".[dev]"
```

### 依存ライブラリ

- Python 3.7以上
- requests
- beautifulsoup4
- aiohttp (非同期機能用)

## 基本的な使い方

### 駅間の経路検索

```python
from yahoosc import YahooTransitAPI

# クライアントの初期化
with YahooTransitAPI() as api:
    # 経路検索の実行
    routes = api.search_routes("服部天神", "新大阪")
    
    # 検索結果の処理
    for route in routes:
        print(f"ルート: {route['route_id']}")
        print(f"出発時刻: {route['departure_time']}")
        print(f"到着時刻: {route['arrival_time']}")
        print(f"所要時間: {route['total_time']}")
        print(f"料金: {route['fare']}")
```

### 駅名候補の取得

```python
from yahoosc import YahooTransitAPI

with YahooTransitAPI() as api:
    # 駅名の候補を取得
    suggestions = api.get_station_suggestions("新宿")
    print(suggestions)
```

## 拡張機能の使い方

### キャッシング機能付きAPI

```python
from yahoosc import EnhancedYahooTransitAPI

# カスタムキャッシュ設定（オプション）
cache_config = {
    "ttl": 3600,  # キャッシュの有効期間（秒）
    "use_file_cache": True,  # ファイルキャッシュを使用
    "cache_dir": "/tmp/yahoosc_cache",  # キャッシュディレクトリ
    "max_memory_entries": 100  # メモリキャッシュの最大エントリ数
}

# キャッシング対応APIクライアントの初期化
with EnhancedYahooTransitAPI(cache_config=cache_config) as api:
    # 初回はAPIから取得され、キャッシュに保存される
    routes = api.search_routes("服部天神", "新大阪")
    
    # 次回以降はキャッシュから高速に取得
    routes_cached = api.search_routes("服部天神", "新大阪")

# キャッシングを無効化するには
with EnhancedYahooTransitAPI(cache_config=False) as api:
    routes = api.search_routes("服部天神", "新大阪")  # 常にAPIから取得
```

### 非同期API（asyncio対応）

```python
import asyncio
from yahoosc import AsyncYahooTransitAPI

async def search_route():
    async with AsyncYahooTransitAPI() as api:
        # 非同期で経路検索
        routes = await api.search_routes_async("服部天神", "新大阪")
        print(f"ルート数: {len(routes)}")
        
        # 並行して複数の駅名候補を取得
        from_task = api.get_station_suggestions_async("東京")
        to_task = api.get_station_suggestions_async("京都")
        
        from_suggestions, to_suggestions = await asyncio.gather(
            from_task, to_task
        )

# 実行
asyncio.run(search_route())
```

### キャッシング対応の非同期API

```python
import asyncio
from yahoosc import AsyncEnhancedYahooTransitAPI

async def main():
    # キャッシング対応の非同期クライアント
    async with AsyncEnhancedYahooTransitAPI() as api:
        # 並行して複数の経路を検索
        routes1 = api.search_routes_async("大阪", "京都")
        routes2 = api.search_routes_async("難波", "三宮")
        routes3 = api.search_routes_async("服部天神", "新大阪")
        
        # 全ての結果を待機
        results = await asyncio.gather(routes1, routes2, routes3)
        
        for i, routes in enumerate(results, 1):
            print(f"経路{i}: {len(routes)}件のルートを取得")

asyncio.run(main())
```

## エラーハンドリング

```python
from yahoosc import YahooTransitAPI, RequestError, ParseError, YahooTransitError

try:
    with YahooTransitAPI() as api:
        routes = api.search_routes("存在しない駅名", "新大阪")
except RequestError as e:
    print(f"HTTPリクエストエラー: {e.status_code} - {e.message}")
except ParseError as e:
    print(f"HTML解析エラー: {e.message}")
except YahooTransitError as e:
    print(f"その他のエラー: {str(e)}")
```

## ロギング機能

```python
import logging
from yahoosc import YahooTransitAPI, logger

# ログレベルを設定
logger.logger.setLevel(logging.DEBUG)

# または環境変数で設定
# YAHOOSC_LOG_LEVEL=DEBUG

with YahooTransitAPI() as api:
    routes = api.search_routes("服部天神", "新大阪")
    # ログにAPIリクエストやレスポンスの詳細が出力される
```

## 使用例

より詳細な使用例については、`yahoosc/examples/` ディレクトリ内のサンプルスクリプトを参照してください。

```bash
# 基本的な検索の例
python -m yahoosc.examples.simple_search

# キャッシング機能の例
python -m yahoosc.examples.enhanced_search

# 非同期処理の例
python -m yahoosc.examples.async_search
```

## 注意事項

このライブラリは非公式であり、Yahoo!路線情報の仕様変更により動作しなくなる可能性があります。商用利用は避け、Yahoo!のサーバーに過度の負荷をかけないようにしてください。あくまで個人的な利用に留めてください。

## ライセンス

MIT License