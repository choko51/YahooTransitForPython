"""
Yahoo!路線情報ライブラリのロギング機能

このモジュールは、ライブラリ内でのロギングを一元管理するための機能を提供します。
"""

import logging
import os
import sys
from typing import Optional

class Logger:
    """ライブラリのロギング機能"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, level=None, log_file=None):
        """シングルトンインスタンスを取得"""
        if cls._instance is None:
            cls._instance = cls(level, log_file)
        return cls._instance
    
    def __init__(self, level=None, log_file=None):
        """ロガーの初期化"""
        self.logger = logging.getLogger("yahoosc")
        
        # すでにハンドラがあれば追加しない
        if self.logger.handlers:
            return
            
        # ログレベルの設定
        log_level = self._get_log_level(level)
        self.logger.setLevel(log_level)
        
        # コンソールへの出力
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # ファイルへの出力（指定がある場合）
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def _get_log_level(self, level=None):
        """ログレベルを取得（環境変数からも取得可能）"""
        if level is not None:
            return level
            
        env_level = os.environ.get("YAHOOSC_LOG_LEVEL", "").upper()
        if env_level == "DEBUG":
            return logging.DEBUG
        elif env_level == "INFO":
            return logging.INFO
        elif env_level == "WARNING":
            return logging.WARNING
        elif env_level == "ERROR":
            return logging.ERROR
        elif env_level == "CRITICAL":
            return logging.CRITICAL
        else:
            return logging.WARNING  # デフォルト
    
    def debug(self, message):
        """デバッグレベルのログを出力"""
        self.logger.debug(message)
    
    def info(self, message):
        """情報レベルのログを出力"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告レベルのログを出力"""
        self.logger.warning(message)
    
    def error(self, message):
        """エラーレベルのログを出力"""
        self.logger.error(message)
    
    def critical(self, message):
        """致命的エラーレベルのログを出力"""
        self.logger.critical(message)

# 使いやすいようにシングルトンインスタンスを事前に作成
logger = Logger.get_instance()