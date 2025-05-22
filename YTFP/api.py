import requests
from .parser import extract_routes_from_html

class YahooTransitAPI:
    """Yahoo!路線情報のAPIクライアント"""
    
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
    
    def __init__(self, headers=None):
        """
        Yahoo!路線情報クライアントを初期化する
        
        Args:
            headers (dict, optional): リクエストに使用するカスタムヘッダー
        """
        self.headers = headers or self.DEFAULT_HEADERS
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_station_suggestions(self, station_query):
        """
        駅名の候補を取得する
        
        Args:
            station_query (str): 検索する駅名の文字列
            
        Returns:
            dict: 駅名候補を含むJSON応答
        """
        response = self.session.get(
            f"{self.SUGGEST_API_URL}?value={station_query}"
        )
        response.raise_for_status()
        return response.json()
    
    def search_routes(self, from_station, to_station, date=None, time=None, via=None, sort=None):
        """
        2駅間の経路を検索する
        
        Args:
            from_station (str): 出発駅
            to_station (str): 到着駅
            date (str, optional): 日付（例: "20250522"）
            time (str, optional): 時刻（例: "0900"）
            via (str, optional): 経由駅
            sort (str, optional): ソート方法（例: "time"）
            
        Returns:
            list: 経路情報のリスト
        """
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
            
        response = self.session.get(self.SEARCH_URL, params=params)
        response.raise_for_status()
        
        # HTMLから経路情報を抽出
        routes = extract_routes_from_html(response.text)
        return routes
        
    def close(self):
        """セッションをクローズする"""
        self.session.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()