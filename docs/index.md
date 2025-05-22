# Yahoo!路線情報ライブラリ ドキュメント

Yahoo!路線情報スクレイピングライブラリ（yahoosc）の公式ドキュメントへようこそ。このドキュメントでは、バージョン0.2.0で導入された技術的改善と機能について詳しく説明します。

## コンテンツ

### 主要ドキュメント

- [技術的改善の概要](technical_improvements.md) - バージョン0.2.0での主な技術的改善の概要
- [キャッシング機能](caching.md) - メモリとファイルベースのキャッシング機能の詳細
- [非同期API](async_api.md) - asyncioベースの非同期処理機能の詳細
- [エラーハンドリング](error_handling.md) - 例外クラス階層と効果的なエラー処理方法
- [ロギング](logging.md) - ログ機能の設定と使用方法

### サンプルコード

サンプルコードは `yahoosc/examples/` ディレクトリにあります：

- `simple_search.py` - 基本的な使用例
- `enhanced_search.py` - キャッシング機能のデモ
- `async_search.py` - 非同期APIのデモ

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/yahoosc.git
cd yahoosc

# ライブラリをインストール
pip install -e .

# 開発用ツールも含めてインストール
pip install -e ".[dev]"
```

## 基本的な使い方

### 標準API

```python
from yahoosc import YahooTransitAPI

with YahooTransitAPI() as api:
    # 経路検索の実行
    routes = api.search_routes("服部天神", "新大阪")
    
    # 検索結果の処理
    for route in routes:
        print(f"ルート: {route['route_id']}")
        print(f"所要時間: {route['total_time']}")
```

### キャッシング対応API

```python
from yahoosc import EnhancedYahooTransitAPI

with EnhancedYahooTransitAPI() as api:
    # 1回目: APIから取得
    routes = api.search_routes("服部天神", "新大阪")
    
    # 2回目: キャッシュから高速に取得
    routes_cached = api.search_routes("服部天神", "新大阪")
```

### 非同期API

```python
import asyncio
from yahoosc import AsyncYahooTransitAPI

async def main():
    async with AsyncYahooTransitAPI() as api:
        # 非同期で経路検索
        routes = await api.search_routes_async("服部天神", "新大阪")
        print(f"ルート数: {len(routes)}")

# 実行
asyncio.run(main())
```

## ライセンス

このライブラリはMITライセンスの下で提供されています。

## 注意事項

このライブラリは非公式であり、Yahoo!路線情報の仕様変更により動作しなくなる可能性があります。商用利用は避け、Yahoo!のサーバーに過度の負荷をかけないようにしてください。あくまで個人的な利用に留めてください。