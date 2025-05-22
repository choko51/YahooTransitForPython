"""
Yahoo!路線情報ライブラリのキャッシング機能

このモジュールは、APIリクエストの結果をキャッシュするための機能を提供します。
メモリ内キャッシュとファイルベースの永続キャッシュの両方をサポートします。
"""

import time
import json
import os
from typing import Dict, Any, Optional, Union, Tuple

class CacheManager:
    """キャッシング機能を提供するクラス"""
    
    def __init__(self, 
                 cache_dir: Optional[str] = None, 
                 ttl: int = 3600,  # デフォルト1時間
                 max_memory_entries: int = 100,
                 use_file_cache: bool = True):
        """
        キャッシュマネージャーの初期化
        
        Args:
            cache_dir: ファイルキャッシュを保存するディレクトリ
            ttl: キャッシュの有効期間（秒）
            max_memory_entries: メモリ内キャッシュの最大エントリ数
            use_file_cache: ファイルキャッシュを使用するかどうか
        """
        self.memory_cache: Dict[str, Tuple[float, Any]] = {}  # (expiry_time, data)
        self.ttl = ttl
        self.max_memory_entries = max_memory_entries
        self.use_file_cache = use_file_cache
        
        if use_file_cache:
            self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".yahoosc_cache")
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_file_path(self, key: str) -> str:
        """キャッシュファイルのパスを取得"""
        import hashlib
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """キャッシュからデータを取得"""
        # メモリキャッシュを確認
        if key in self.memory_cache:
            expiry_time, data = self.memory_cache[key]
            if expiry_time > time.time():
                return data
            # 期限切れの場合は削除
            del self.memory_cache[key]
        
        # ファイルキャッシュを確認
        if self.use_file_cache:
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # 有効期限をチェック
                    if cache_data.get('expiry', 0) > time.time():
                        # メモリキャッシュにも追加
                        self.memory_cache[key] = (cache_data['expiry'], cache_data['data'])
                        return cache_data['data']
                    else:
                        # 期限切れのファイルを削除
                        os.remove(cache_file)
                except (json.JSONDecodeError, KeyError, OSError):
                    pass
        
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """データをキャッシュに設定"""
        expiry_time = time.time() + (ttl or self.ttl)
        
        # メモリキャッシュが最大サイズに達した場合、最も古いエントリを削除
        if len(self.memory_cache) >= self.max_memory_entries:
            oldest_key = min(self.memory_cache.keys(), 
                            key=lambda k: self.memory_cache[k][0])
            del self.memory_cache[oldest_key]
        
        # メモリキャッシュに追加
        self.memory_cache[key] = (expiry_time, data)
        
        # ファイルキャッシュに保存
        if self.use_file_cache:
            cache_file = self._get_cache_file_path(key)
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'expiry': expiry_time,
                        'data': data
                    }, f, ensure_ascii=False)
            except OSError:
                pass  # ファイル書き込みエラーは無視
    
    def invalidate(self, key: str) -> None:
        """特定のキーのキャッシュを無効化"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        if self.use_file_cache:
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except OSError:
                    pass
    
    def clear(self) -> None:
        """全てのキャッシュをクリア"""
        self.memory_cache.clear()
        
        if self.use_file_cache:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    try:
                        os.remove(os.path.join(self.cache_dir, filename))
                    except OSError:
                        pass