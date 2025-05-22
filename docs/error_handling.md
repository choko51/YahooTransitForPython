# エラーハンドリング

Yahoo!路線情報ライブラリのエラーハンドリング機能について説明します。

## 概要

エラーハンドリング機能は、ライブラリ内で発生する可能性のある様々なエラー状況に対して、より詳細な情報とより適切な対処方法を提供します。バージョン0.2.0では、専用の例外クラス階層を導入し、エラーの種類に応じた例外処理を可能にしています。

## 例外クラス階層

Yahoo!路線情報ライブラリでは、以下の例外クラス階層を使用しています：

```
YahooTransitError  # 基本例外クラス
├── RequestError  # HTTPリクエスト関連のエラー
├── ParseError  # HTML解析関連のエラー
├── RateLimitError  # レート制限関連のエラー
├── ConfigurationError  # 設定関連のエラー
└── CacheError  # キャッシュ操作関連のエラー
```

## 各例外クラスの詳細

### YahooTransitError

ライブラリの基本例外クラスです。他のすべての例外クラスはこのクラスを継承しています。

```python
try:
    # ライブラリの機能を使用
    with YahooTransitAPI() as api:
        routes = api.search_routes("東京", "大阪")
except YahooTransitError as e:
    # すべてのライブラリ例外をキャッチ
    print(f"エラーが発生しました: {str(e)}")
```

### RequestError

HTTPリクエスト時に発生するエラーを表します。ステータスコードとエラーメッセージを含みます。

```python
try:
    with YahooTransitAPI() as api:
        routes = api.search_routes("存在しない駅名", "新大阪")
except RequestError as e:
    print(f"HTTPエラー {e.status_code}: {e.message}")
    if e.status_code == 404:
        print("指定された駅名が見つかりませんでした")
    elif e.status_code == 500:
        print("サーバー側でエラーが発生しました")
```

### ParseError

HTML解析時に発生するエラーを表します。エラーメッセージと、オプションでソースHTMLの一部を含みます。

```python
try:
    with YahooTransitAPI() as api:
        routes = api.search_routes("服部天神", "新大阪")
except ParseError as e:
    print(f"HTML解析エラー: {e.message}")
    if hasattr(e, 'source') and e.source:
        print(f"問題のソース: {e.source[:100]}...")  # 最初の100文字のみ表示
```

### RateLimitError

APIのレート制限に達したときに発生するエラーを表します。可能であれば再試行までの待機時間を含みます。

```python
try:
    # 多数のリクエストを実行
    for i in range(100):
        with YahooTransitAPI() as api:
            routes = api.search_routes(f"駅{i}", "東京")
except RateLimitError as e:
    print(f"レート制限エラー: {str(e)}")
    if e.retry_after:
        print(f"{e.retry_after}秒後に再試行してください")
    else:
        print("しばらく経ってから再試行してください")
```

### ConfigurationError

設定の問題に関するエラーを表します。キャッシュディレクトリのパーミッション問題など、設定関連の問題で発生します。

```python
try:
    # 無効な設定でAPIを初期化
    with EnhancedYahooTransitAPI(cache_config={"cache_dir": "/root/invalid"}) as api:
        routes = api.search_routes("東京", "大阪")
except ConfigurationError as e:
    print(f"設定エラー: {str(e)}")
```

### CacheError

キャッシュ操作に関するエラーを表します。キャッシュの読み書きや削除の問題で発生します。

```python
try:
    cache_config = {"cache_dir": "/path/to/nonexistent/directory"}
    with EnhancedYahooTransitAPI(cache_config=cache_config) as api:
        routes = api.search_routes("東京", "大阪")
except CacheError as e:
    print(f"キャッシュエラー: {str(e)}")
    # キャッシングを無効化して再試行
    with EnhancedYahooTransitAPI(cache_config=False) as api:
        routes = api.search_routes("東京", "大阪")
```

## エラーハンドリングのベストプラクティス

### 段階的な例外キャッチ

エラーの種類に応じて異なる対処を行うために、段階的に例外をキャッチします：

```python
try:
    with YahooTransitAPI() as api:
        routes = api.search_routes("東京", "大阪")
except RequestError as e:
    print(f"通信エラー: {e.status_code} - {e.message}")
    # 通信エラーの対処
except ParseError as e:
    print(f"解析エラー: {e.message}")
    # 解析エラーの対処
except YahooTransitError as e:
    print(f"その他のライブラリエラー: {str(e)}")
    # その他のエラーの対処
except Exception as e:
    print(f"予期しないエラー: {str(e)}")
    # 未知のエラーの対処
```

### バリケード・パターンの使用

ライブラリのエラーを呼び出し元に漏らさないようにする「バリケード・パターン」も有効です：

```python
def get_route_info(from_station, to_station):
    """経路情報を取得し、エラーを適切に処理する"""
    try:
        with YahooTransitAPI() as api:
            routes = api.search_routes(from_station, to_station)
            return {
                "success": True,
                "routes": routes,
                "error": None
            }
    except RequestError as e:
        return {
            "success": False,
            "routes": [],
            "error": f"通信エラー: {e.status_code} - {e.message}"
        }
    except ParseError as e:
        return {
            "success": False,
            "routes": [],
            "error": f"データ解析エラー: {e.message}"
        }
    except YahooTransitError as e:
        return {
            "success": False,
            "routes": [],
            "error": f"API呼び出しエラー: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "routes": [],
            "error": f"未知のエラー: {str(e)}"
        }
```

### エラーロギングとの連携

エラーハンドリングとロギングを組み合わせることで、問題の追跡と分析が容易になります：

```python
from yahoosc import YahooTransitAPI, RequestError, ParseError, logger

try:
    with YahooTransitAPI() as api:
        routes = api.search_routes("東京", "大阪")
except RequestError as e:
    logger.error(f"APIリクエストエラー: {e.status_code} - {e.message}")
    # エラー対処
except ParseError as e:
    logger.error(f"HTMLパースエラー: {e.message}")
    if hasattr(e, 'source') and e.source:
        logger.debug(f"問題のソース: {e.source}")
    # エラー対処
except Exception as e:
    logger.critical(f"予期しないエラー: {str(e)}", exc_info=True)
    # エラー対処
```

## エラーケース別の対処方法

### ネットワーク接続の問題

一時的なネットワーク接続の問題には、リトライ戦略が効果的です：

```python
import time
from yahoosc import YahooTransitAPI, RequestError

def get_routes_with_retry(from_station, to_station, max_retries=3, delay=2):
    """リトライ機能付きの経路検索"""
    retries = 0
    while retries < max_retries:
        try:
            with YahooTransitAPI() as api:
                return api.search_routes(from_station, to_station)
        except RequestError as e:
            if e.status_code in (503, 504, 408):  # サーバー一時的エラーや接続タイムアウト
                retries += 1
                if retries < max_retries:
                    wait_time = delay * (2 ** (retries - 1))  # 指数バックオフ
                    print(f"接続エラー: {wait_time}秒後に再試行します ({retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"最大再試行回数に達しました: {e}")
                    raise
            else:
                # 一時的なエラーではない場合はそのまま再送出
                raise
```

### HTMLの構造変更への対応

Webサイトの構造変更に対処するためのエラーハンドリング：

```python
from yahoosc import YahooTransitAPI, ParseError, logger

try:
    with YahooTransitAPI() as api:
        routes = api.search_routes("東京", "大阪")
except ParseError as e:
    if "could not find element with selector" in str(e).lower():
        logger.critical("Yahoo!路線情報のHTML構造が変更された可能性があります")
        # 代替手段があれば実行
    else:
        logger.error(f"HTML解析エラー: {e}")
```

### レート制限への対応

APIの過剰な使用によるレート制限への対処：

```python
from yahoosc import YahooTransitAPI, RateLimitError, logger
import time

try:
    with YahooTransitAPI() as api:
        # 多数のリクエストを実行
        for station in stations_list:
            routes = api.search_routes(station, "東京")
except RateLimitError as e:
    logger.warning(f"レート制限に達しました: {e}")
    
    # 待機時間がある場合は待機して再試行
    if hasattr(e, 'retry_after') and e.retry_after:
        logger.info(f"{e.retry_after}秒間待機します")
        time.sleep(e.retry_after)
        
        # 再試行
        with YahooTransitAPI() as api:
            routes = api.search_routes("東京", "大阪")
```

## エラーハンドリングと非同期API

非同期APIを使用する場合のエラーハンドリング：

```python
import asyncio
from yahoosc import AsyncYahooTransitAPI, RequestError, ParseError

async def safe_search_routes(from_station, to_station):
    """エラーハンドリング付きの非同期経路検索"""
    try:
        async with AsyncYahooTransitAPI() as api:
            return await api.search_routes_async(from_station, to_station)
    except RequestError as e:
        print(f"リクエストエラー: {e.status_code} - {e.message}")
        return []
    except ParseError as e:
        print(f"解析エラー: {e.message}")
        return []
    except Exception as e:
        print(f"その他のエラー: {str(e)}")
        return []

async def main():
    routes = await safe_search_routes("東京", "大阪")
    if routes:
        print(f"{len(routes)}件のルートが見つかりました")
    else:
        print("ルートが見つかりませんでした")

asyncio.run(main())
```

## エラーリファレンス

各エラークラスの詳細情報とそれが発生する可能性のある状況を示します：

| エラークラス | 発生する可能性のある状況 | 推奨される対処方法 |
|------------|---------------------|-----------------|
| `RequestError` | ネットワーク接続の問題、無効なURLやリクエスト、サーバーエラー | 一時的なエラーの場合は再試行、永続的なエラーの場合はリクエストを確認 |
| `ParseError` | HTML構造の変更、不完全なHTMLレスポンス、セレクタの不一致 | ライブラリの更新を確認、代替データソースを検討 |
| `RateLimitError` | 短時間における過剰なAPIリクエスト | レート制限に従って待機、リクエスト頻度を下げる |
| `ConfigurationError` | 無効な設定パラメータ、権限の問題 | 設定を見直し、権限を確認 |
| `CacheError` | キャッシュディレクトリの書き込み権限の問題、ディスク容量不足 | ディレクトリのパーミッションを確認、ディスク容量を確保、またはキャッシングを無効化 |