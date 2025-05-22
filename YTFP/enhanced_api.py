"""
Yahoo!路線情報ライブラリの拡張API

このモジュールは、キャッシング機能や拡張エラーハンドリングなどを備えた
拡張Yahoo!路線情報APIクライアントを提供します。
"""

import hashlib
import json
from typing import Dict, List, Any, Optional, Union

from .api import YahooTransitAPI
from .cache import CacheManager
from .errors import RequestError, ParseError, YahooTransitError
from .logger import logger

class EnhancedYahooTransitAPI(YahooTransitAPI):
    """キャッシング機能を持つYahoo!路線情報APIクライアント"""
    
    def __init__(self, headers=None, cache_config=None):
        """
        拡張APIクライアントの初期化
        
        Args:
            headers: カスタムHTTPヘッダー
            cache_config: キャッシュ設定
                - None: デフォルト設定でキャッシングを有効化
                - False: キャッシングを無効化
                - dict: キャッシュの詳細設定（CacheManagerのパラメータ）
        """
        super().__init__(headers)
        
        # キャッシュを無効化したい場合はcache_config=Falseを指定
        if cache_config is not False:
            self.cache = CacheManager(**(cache_config or {}))
            logger.info("キャッシングが有効化されました")
        else:
            self.cache = None
            logger.info("キャッシングが無効化されました")
    
    def _get_cache_key(self, method: str, **params) -> str:
        """パラメータからキャッシュキーを生成"""
        # パラメータをソートしてJSON文字列化
        param_str = json.dumps(params, sort_keys=True)
        return f"{method}:{hashlib.md5(param_str.encode()).hexdigest()}"
    
    def get_station_suggestions(self, station_query: str) -> Dict[str, Any]:
        """
        駅名候補を取得（キャッシング対応）
        
        Args:
            station_query: 検索する駅名の文字列
            
        Returns:
            dict: 駅名候補を含むJSON応答
            
        Raises:
            RequestError: HTTPリクエストでエラーが発生した場合
            YahooTransitError: その他のエラーが発生した場合
        """
        # キャッシングが無効なら通常の処理
        if not self.cache:
            return super().get_station_suggestions(station_query)
        
        # キャッシュキーの生成
        cache_key = self._get_cache_key("suggestions", query=station_query)
        cached_result = self.cache.get(cache_key)
        
        # キャッシュヒット時はキャッシュから返す
        if cached_result is not None:
            logger.debug(f"キャッシュヒット: {cache_key}")
            return cached_result
        
        try:
            # 通常のAPIリクエスト
            logger.debug(f"APIリクエスト: 駅名候補取得 '{station_query}'")
            result = super().get_station_suggestions(station_query)
            
            # 結果をキャッシュに保存
            self.cache.set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"駅名候補取得エラー: {str(e)}")
            # 元の例外を保持して再送出
            raise
    
    def search_routes(self, from_station: str, to_station: str, **kwargs) -> List[Dict[str, Any]]:
        """
        経路検索（キャッシング対応）
        
        Args:
            from_station: 出発駅
            to_station: 到着駅
            **kwargs: その他のパラメータ
                - date: 日付（例: "20250522"）
                - time: 時刻（例: "0900"）
                - via: 経由駅
                - sort: ソート方法
                
        Returns:
            list: 経路情報のリスト
            
        Raises:
            RequestError: HTTPリクエストでエラーが発生した場合
            ParseError: HTML解析でエラーが発生した場合
            YahooTransitError: その他のエラーが発生した場合
        """
        # キャッシングが無効なら通常の処理
        if not self.cache:
            return super().search_routes(from_station, to_station, **kwargs)
        
        # キャッシュキーの生成
        cache_key = self._get_cache_key("routes", 
                                     from_station=from_station, 
                                     to_station=to_station, 
                                     **kwargs)
        cached_result = self.cache.get(cache_key)
        
        # キャッシュヒット時はキャッシュから返す
        if cached_result is not None:
            logger.debug(f"キャッシュヒット: {cache_key}")
            return cached_result
        
        try:
            # 通常のAPIリクエスト
            logger.debug(f"APIリクエスト: 経路検索 '{from_station}' -> '{to_station}'")
            result = super().search_routes(from_station, to_station, **kwargs)
            
            # 結果をキャッシュに保存
            self.cache.set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"経路検索エラー: {str(e)}")
            # 元の例外を保持して再送出
            raise