# ロギング機能

Yahoo!路線情報ライブラリのロギング機能について説明します。

## 概要

ロギング機能は、ライブラリの動作状況や問題を追跡するための機能です。デバッグ情報の出力、情報メッセージ、警告、エラーなどを適切に記録することで、アプリケーションの動作状況の把握や問題解決に役立ちます。

Yahoo!路線情報ライブラリでは、Python標準の`logging`モジュールをベースに、使いやすいインターフェースを提供しています。

## 基本的な使い方

### ロガーへのアクセス

ライブラリには、事前に設定されたロガーインスタンスが含まれています：

```python
from yahoosc import logger

# ロガーを使用してメッセージを出力
logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

### ログレベルの設定

ログレベルを変更することで、出力されるログの詳細度を制御できます：

```python
import logging
from yahoosc import logger

# ログレベルをDEBUGに設定（より詳細なログを出力）
logger.logger.setLevel(logging.DEBUG)

# または直接
logger.logger.setLevel(10)  # DEBUGレベルは10
```

利用可能なログレベル（重要度の低い順）：

1. `DEBUG` (10) - 詳細なデバッグ情報
2. `INFO` (20) - 一般的な情報メッセージ
3. `WARNING` (30) - 警告メッセージ（デフォルト）
4. `ERROR` (40) - エラーメッセージ
5. `CRITICAL` (50) - 致命的なエラーメッセージ

### ロギングの実例

APIリクエストの流れを追跡する例：

```python
from yahoosc import YahooTransitAPI, logger
import logging

# ログレベルをDEBUGに設定
logger.logger.setLevel(logging.DEBUG)

logger.info("経路検索を開始します")
try:
    with YahooTransitAPI() as api:
        logger.debug(f"APIクライアントを初期化しました")
        
        logger.info(f"'服部天神'から'新大阪'への経路を検索します")
        routes = api.search_routes("服部天神", "新大阪")
        
        logger.info(f"{len(routes)}件のルートが見つかりました")
        for i, route in enumerate(routes):
            logger.debug(f"ルート{i+1}: {route.get('route_id', f'ルート {i+1}')}")
except Exception as e:
    logger.error(f"経路検索中にエラーが発生しました: {str(e)}")
    logger.debug("エラーの詳細:", exc_info=True)  # スタックトレースを出力
finally:
    logger.info("経路検索を終了します")
```

## 環境変数による設定

ログレベルは環境変数を使って設定することもできます：

```bash
# Windowsの場合
set YAHOOSC_LOG_LEVEL=DEBUG
python my_script.py

# Linuxの場合
YAHOOSC_LOG_LEVEL=DEBUG python my_script.py
```

ライブラリは起動時に`YAHOOSC_LOG_LEVEL`環境変数を確認し、ログレベルを設定します。有効な値は次のとおりです：

- `DEBUG`
- `INFO`
- `WARNING` (デフォルト)
- `ERROR`
- `CRITICAL`

## ファイルへのログ出力

ログをファイルに出力するには、新しいロガーインスタンスを作成します：

```python
from yahoosc import Logger
import logging

# ファイルにログを出力するロガーを作成
file_logger = Logger.get_instance(
    level=logging.DEBUG,
    log_file="yahoosc.log"  # 出力先ファイル
)

# ログの出力
file_logger.info("このメッセージはファイルに記録されます")
file_logger.error("エラーメッセージもファイルに記録されます")
```

## 複数の出力先への同時ログ記録

コンソールとファイルの両方にログを出力する場合：

```python
import logging
import sys
from yahoosc import logger

# 既存のロガーにファイル出力を追加
file_handler = logging.FileHandler("yahoosc.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# ロガーにハンドラを追加
logger.logger.addHandler(file_handler)

# ログ出力（コンソールとファイルの両方に出力される）
logger.info("このメッセージは両方に記録されます")
```

## APIクラスのロギング動作

Yahoo!路線情報ライブラリの各APIクラスは、内部でロガーを使用して動作状況を記録します：

### 主なログポイント

1. **リクエスト開始時**：
   ```
   DEBUG: APIリクエスト: 駅名候補取得 '東京'
   ```

2. **キャッシュヒット時**：
   ```
   DEBUG: キャッシュヒット: suggestions:a1b2c3d4e5...
   ```

3. **エラー発生時**：
   ```
   ERROR: 経路検索エラー: HTTPエラー 404 - Not Found
   ```

4. **初期化時**：
   ```
   INFO: キャッシングが有効化されました
   ```

## カスタムロガーの作成

特定のニーズに合わせてカスタムロガーを作成することができます：

```python
import logging
from yahoosc.logger import Logger

# カスタマイズされたロガーを作成
def create_custom_logger(name, log_file=None):
    # 基本ロガーの取得
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(logging.INFO)
    
    # コンソールハンドラの追加
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s [%(name)s]: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger_instance.addHandler(console_handler)
    
    # ファイルハンドラの追加（オプション）
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # ファイルにはより詳細なログを出力
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger_instance.addHandler(file_handler)
    
    return logger_instance

# カスタムロガーの使用
my_logger = create_custom_logger("my_app", "my_app.log")
my_logger.info("アプリケーションを開始します")

# Yahoo!路線情報ライブラリの使用
from yahoosc import YahooTransitAPI
with YahooTransitAPI() as api:
    routes = api.search_routes("東京", "大阪")
    my_logger.info(f"{len(routes)}件のルートが見つかりました")
```

## アプリケーションログとの統合

アプリケーションの既存のロギング設定とYahoo!路線情報ライブラリのロギングを統合する場合：

```python
import logging

# アプリケーションのロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# ライブラリのロガーを設定
from yahoosc import logger
logger.logger.setLevel(logging.INFO)  # ライブラリのログレベルを設定

# ライブラリとアプリケーションのロガーが同じ形式で出力
app_logger = logging.getLogger("my_app")
app_logger.info("アプリケーションログ")
logger.info("ライブラリログ")
```

## エラーハンドリングとの連携

エラーハンドリングとロギングを組み合わせることで、エラー追跡と分析が容易になります：

```python
from yahoosc import YahooTransitAPI, RequestError, ParseError, logger
import logging

# ログレベルを設定
logger.logger.setLevel(logging.DEBUG)

try:
    with YahooTransitAPI() as api:
        logger.info("経路検索を開始します")
        routes = api.search_routes("存在しない駅名", "新大阪")
except RequestError as e:
    logger.error(f"APIリクエストエラー: {e.status_code} - {e.message}")
    # エラー処理
except ParseError as e:
    logger.error(f"HTML解析エラー: {e.message}")
    logger.debug(f"問題のHTML: {e.source[:100]}..." if hasattr(e, 'source') and e.source else "なし")
    # エラー処理
except Exception as e:
    logger.critical(f"予期しないエラー: {str(e)}", exc_info=True)
    # エラー処理
finally:
    logger.info("経路検索処理を終了します")
```

## パフォーマンスの考慮事項

ロギングは便利ですが、特に`DEBUG`レベルのログを大量に出力すると、パフォーマンスに影響を与える可能性があります。本番環境では適切なログレベルを設定することが重要です：

```python
import os
from yahoosc import logger
import logging

# 環境に応じてログレベルを設定
if os.environ.get('ENVIRONMENT') == 'production':
    logger.logger.setLevel(logging.WARNING)  # 本番環境では警告以上のみ
elif os.environ.get('ENVIRONMENT') == 'staging':
    logger.logger.setLevel(logging.INFO)  # ステージング環境では情報以上
else:
    logger.logger.setLevel(logging.DEBUG)  # 開発環境ではすべてのログ
```

## ロギングのベストプラクティス

### 適切なログレベルの使用

各ログレベルの適切な使用方法：

- **DEBUG**: 詳細なデバッグ情報（リクエストの詳細、パラメータの値など）
- **INFO**: 一般的な情報（処理の開始と終了、主要な処理ステップなど）
- **WARNING**: 潜在的な問題（遅いレスポンス、非推奨機能の使用など）
- **ERROR**: エラー状態（リクエスト失敗、解析エラーなど）
- **CRITICAL**: 致命的な問題（接続不能、データ破損など）

### コンテキスト情報の含有

エラーの原因を特定しやすくするために、十分なコンテキスト情報をログに含めます：

```python
# 不十分なログ
logger.error("経路検索に失敗しました")

# 改善されたログ（コンテキスト情報を含む）
logger.error(f"経路検索に失敗しました: '{from_station}'から'{to_station}'への経路")
```

### センシティブ情報の保護

ログにセンシティブ情報を含めないように注意します：

```python
# 悪い例（APIキーがログに記録される）
logger.debug(f"APIリクエスト: {url}?api_key={api_key}")

# 良い例
logger.debug(f"APIリクエスト: {url}?api_key=***")
```

## ログファイルの管理

長期間運用する場合は、ログローテーションを考慮することも重要です：

```python
import logging
from logging.handlers import RotatingFileHandler

# ログローテーション設定
handler = RotatingFileHandler(
    "yahoosc.log",
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5  # 最大5つのバックアップファイル
)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# ロガーにハンドラを追加
from yahoosc import logger
logger.logger.addHandler(handler)
```

これにより、ログファイルが10MBに達すると自動的にローテーションされ、最大5つのバックアップファイルが保持されます。