"""
Yahoo!路線情報ライブラリの非同期API

このモジュールは、Yahoo!路線情報へのアクセスを非同期で行うためのクラスを提供します。
aiohttp を使用して非同期HTTPリクエストを実行します。
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional, Any

from .parser import extract_routes_from_html

class AsyncYahooTransitAPI:
    """Yahoo!路線情報の非同期APIクライアント"""
    
    # 基本的なヘッダーと定数
    DEFAULT_HEADERS = {
        "authority": "transit.yahoo.co.jp",
        "method": "GET",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://transit.yahoo.co.jp/",
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-platform-version": '"19.0.0"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    
    BASE_URL = "https://transit.yahoo.co.jp"
    SUGGEST_API_URL = f"{BASE_URL}/api/suggest"
    SEARCH_URL = f"{BASE_URL}/search/result"
    
    def __init__(self, headers=None, session=None):
        """
        非同期クライアントの初期化
        
        Args:
            headers: カスタムHTTPヘッダー
            session: 既存のaiohttp.ClientSession（指定しない場合は新規作成）
        """
        self.headers = headers or self.DEFAULT_HEADERS
        self._session = session
        self._owned_session = session is None
    
    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリーポイント"""
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了処理"""
        if self._owned_session and self._session is not None:
            await self._session.close()
    
    async def _ensure_session(self):
        """セッションが存在することを確認"""
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.headers)
            self._owned_session = True
    
    async def get_station_suggestions_async(self, station_query: str) -> Dict[str, Any]:
        """
        駅名の候補を非同期に取得する
        
        Args:
            station_query: 検索する駅名の文字列
            
        Returns:
            dict: 駅名候補を含むJSON応答
        """
        await self._ensure_session()
            
        async with self._session.get(
            f"{self.SUGGEST_API_URL}?value={station_query}"
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def search_routes_async(self, from_station: str, to_station: str, 
                                date: Optional[str] = None,
                                time: Optional[str] = None,
                                via: Optional[str] = None,
                                sort: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        2駅間の経路を非同期に検索する
        
        Args:
            from_station: 出発駅
            to_station: 到着駅
            date: 日付（例: "20250522"）
            time: 時刻（例: "0900"）
            via: 経由駅
            sort: ソート方法（例: "time"）
            
        Returns:
            list: 経路情報のリスト
        """
        await self._ensure_session()
            
        params = {
            "from": from_station,
            "to": to_station
        }
        
        # オプションパラメータの追加
        if date:
            params["date"] = date
        if time:
            params["time"] = time
        if via:
            params["via"] = via
        if sort:
            params["sort"] = sort
        
        async with self._session.get(self.SEARCH_URL, params=params) as response:
            response.raise_for_status()
            html = await response.text()
            # 現状ではパース処理は同期的に行う
            # 注: 将来的に非同期パーサーを実装する可能性あり
            return extract_routes_from_html(html)
    
    async def close(self):
        """セッションを閉じる"""
        if self._session is not None and self._owned_session:
            await self._session.close()
            self._session = None