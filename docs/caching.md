# キャッシング機能

Yahoo!路線情報ライブラリのキャッシング機能について説明します。

## 概要

キャッシング機能は、APIリクエストの結果をローカルに保存し、同じリクエストが再度行われた場合に高速に結果を返すことができます。これにより、特に同じリクエストを何度も実行する場合に大幅なパフォーマンス向上が期待できます。

キャッシングには以下のタイプがサポートされています：
- **メモリキャッシュ** - メモリ内に一時的にデータを保存
- **ファイルキャッシュ** - ファイルシステムにデータを永続的に保存

## 基本的な使い方

### EnhancedYahooTransitAPIの使用

キャッシング機能を使用するには、標準の`YahooTransitAPI`の代わりに`EnhancedYahooTransitAPI`クラスを使用します：

```python
from yahoosc import EnhancedYahooTransitAPI

# デフォルト設定でキャッシングを有効化
with EnhancedYahooTransitAPI() as api:
    # 1回目のリクエスト - APIから取得され、キャッシュに保存
    routes = api.search_routes("服部天神", "新大阪")
    
    # 2回目のリクエスト - キャッシュから高速に取得
    routes_again = api.search_routes("服部天神", "新大阪")
```

### 非同期APIでのキャッシング

非同期APIでもキャッシング機能を使用できます：

```python
import asyncio
from yahoosc import AsyncEnhancedYahooTransitAPI

async def main():
    async with AsyncEnhancedYahooTransitAPI() as api:
        # 1回目のリクエスト - APIから取得
        routes = await api.search_routes_async("服部天神", "新大阪")
        
        # 2回目のリクエスト - キャッシュから取得
        routes_again = await api.search_routes_async("服部天神", "新大阪")

asyncio.run(main())
```

## 詳細設定

キャッシュの動作はコンストラクタの`cache_config`パラメータで詳細に設定できます：

```python
from yahoosc import EnhancedYahooTransitAPI

# キャッシュの詳細設定
cache_config = {
    "ttl": 3600,                   # キャッシュの有効期間（秒）
    "max_memory_entries": 100,     # メモリキャッシュの最大エントリ数
    "use_file_cache": True,        # ファイルキャッシュを有効化/無効化
    "cache_dir": "/tmp/yahoosc_cache"  # ファイルキャッシュのディレクトリ
}

with EnhancedYahooTransitAPI(cache_config=cache_config) as api:
    # APIリクエスト実行
    routes = api.search_routes("服部天神", "新大阪")
```

### 設定オプション

| 設定項目 | 説明 | デフォルト値 |
|---------|------|------------|
| `ttl` | キャッシュの有効期間（秒） | 3600（1時間） |
| `max_memory_entries` | メモリキャッシュの最大エントリ数 | 100 |
| `use_file_cache` | ファイルキャッシュを使用するかどうか | True |
| `cache_dir` | ファイルキャッシュを保存するディレクトリ | ~/.yahoosc_cache |

### キャッシングの無効化

特定のユースケースでキャッシングを無効化する場合は、`cache_config=False`を指定します：

```python
# キャッシングを無効化
with EnhancedYahooTransitAPI(cache_config=False) as api:
    # 常にAPIから取得
    routes = api.search_routes("服部天神", "新大阪")
```

## 直接CacheManagerの使用

より高度なユースケースでは、`CacheManager`クラスを直接使用することもできます：

```python
from yahoosc.cache import CacheManager

# キャッシュマネージャーのインスタンス化
cache = CacheManager(ttl=1800, use_file_cache=True)

# データの保存
cache.set("my_key", {"data": "value"})

# データの取得
data = cache.get("my_key")
if data is not None:
    print("キャッシュヒット:", data)
else:
    print("キャッシュミス")
    
# キャッシュの無効化
cache.invalidate("my_key")

# すべてのキャッシュをクリア
cache.clear()
```

## 内部の仕組み

### キャッシュキーの生成

キャッシュキーは、メソッド名とパラメータのハッシュから生成されます：

```python
def _get_cache_key(self, method: str, **params) -> str:
    """パラメータからキャッシュキーを生成"""
    import hashlib
    import json
    
    # パラメータをソートしてJSON文字列化
    param_str = json.dumps(params, sort_keys=True)
    return f"{method}:{hashlib.md5(param_str.encode()).hexdigest()}"
```

### キャッシュの保存場所

ファイルキャッシュは、指定されたキャッシュディレクトリ（デフォルトでは`~/.yahoosc_cache`）にJSONファイルとして保存されます。各キャッシュエントリは独立したファイルとして、キーのMD5ハッシュ値をファイル名として保存されます。

### キャッシュの有効期限

各キャッシュエントリには有効期限（TTL）が設定されます。有効期限が切れたキャッシュエントリは、取得時に自動的に削除され、新しいデータがAPIから取得されます。

## パフォーマンスの考慮事項

- メモリキャッシュは最も高速ですが、プロセス終了時に失われます
- ファイルキャッシュはプロセス間で共有できますが、メモリキャッシュよりは低速です
- 大量のデータをキャッシュする場合は、`max_memory_entries`を適切に設定してメモリ使用量を制御してください
- 時間によって変動するデータ（経路検索結果など）の場合、適切なTTL値を設定することで、リアルタイム性とパフォーマンスのバランスを取ることができます