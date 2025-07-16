"""
Co-Analyst AI プロトタイプ設定ファイル
"""
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Config:
    # プロジェクトパス
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, "knowledge_base")
    DATA_PATH = os.path.join(PROJECT_ROOT, "data")
    OUTPUT_PATH = os.path.join(PROJECT_ROOT, "outputs")
    EXECUTION_PATH = os.path.join(PROJECT_ROOT, "execution")
    
    # LLM設定（デモ用にOpenAI APIを使用、実際はローカルLlamaに置き換え）
    LLM_MODEL = "gpt-3.5-turbo"  # 実際の実装ではLlama3に変更
    LLM_TEMPERATURE = 0.3
    MAX_TOKENS = 2048
    
    # RAG設定
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DB_PATH = os.path.join(PROJECT_ROOT, "vector_db")
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    
    # コード実行設定
    PYTHON_EXECUTABLE = "python"
    CODE_TIMEOUT = 30  # 秒
    SANDBOX_MODE = True
    
    # UI設定
    STREAMLIT_PORT = 8501
    API_PORT = 8000
    
    # ログ設定
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "co_analyst.log")

# グローバル設定インスタンス
config = Config()
