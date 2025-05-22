"""
Yahoo!路線情報スクレイピングライブラリ

このパッケージは、Yahoo!路線情報から経路情報を取得するためのユーティリティを提供します。
キャッシング機能と非同期処理に対応したAPIも含まれています。
"""

# 基本コンポーネント
from .api import YahooTransitAPI
from .parser import extract_routes_from_html, extract_route_info

# 拡張API（キャッシング対応）
from .enhanced_api import EnhancedYahooTransitAPI

# 非同期API
from .async_api import AsyncYahooTransitAPI
from .async_enhanced_api import AsyncEnhancedYahooTransitAPI

# エラー定義
from .errors import YahooTransitError, RequestError, ParseError, RateLimitError

# ユーティリティ
from .cache import CacheManager
from .logger import Logger, logger

__version__ = "0.2.0"
__all__ = [
    # 基本コンポーネント
    "YahooTransitAPI",
    "extract_routes_from_html",
    "extract_route_info",
    
    # 拡張API
    "EnhancedYahooTransitAPI",
    
    # 非同期API
    "AsyncYahooTransitAPI",
    "AsyncEnhancedYahooTransitAPI",
    
    # エラー
    "YahooTransitError",
    "RequestError",
    "ParseError",
    "RateLimitError",
    
    # ユーティリティ
    "CacheManager",
    "Logger",
    "logger"
]