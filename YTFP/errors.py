"""
Yahoo!路線情報ライブラリのエラー定義

このモジュールは、ライブラリで使用される例外クラスを定義します。
適切なエラー処理が可能になります。
"""

class YahooTransitError(Exception):
    """Yahoo!路線情報APIの基本エラー"""
    pass

class RequestError(YahooTransitError):
    """HTTPリクエストエラー"""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP Error {status_code}: {message}")

class ParseError(YahooTransitError):
    """HTML解析エラー"""
    def __init__(self, message, source=None):
        self.message = message
        self.source = source
        error_msg = f"Parse Error: {message}"
        if source:
            error_msg += f" (source: {source[:100]}...)" if len(source) > 100 else f" (source: {source})"
        super().__init__(error_msg)

class RateLimitError(YahooTransitError):
    """レート制限エラー"""
    def __init__(self, retry_after=None):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after} seconds"
        super().__init__(message)

class ConfigurationError(YahooTransitError):
    """設定エラー"""
    pass

class CacheError(YahooTransitError):
    """キャッシュ操作に関するエラー"""
    pass