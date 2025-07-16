"""
コード実行環境
生成されたコード（Python）を安全に実行し、
その標準出力、エラー出力、結果データを取得する環境
"""
import os
import sys
import subprocess
import tempfile
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import config

class CodeExecutor:
    """コード実行を管理するクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.execution_history = []
        
    def execute(self, code_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        コードを実行
        
        Args:
            code_info: 実行するコードとメタデータ
            
        Returns:
            実行結果
        """
        self.logger.info(f"コード実行開始: {code_info['method_name']}")
        
        code = code_info["code"]
        execution_id = self._generate_execution_id()
        
        # 実行環境の準備
        execution_env = self._prepare_execution_environment()
        
        # コードファイルの作成
        code_file_path = self._create_code_file(code, execution_id)
        
        try:
            # コード実行
            result = self._run_code(code_file_path, execution_env)
            
            # 結果の後処理
            processed_result = self._process_execution_result(result, code_info)
            
            # 実行履歴に記録
            self._record_execution(execution_id, code_info, processed_result)
            
            return processed_result
            
        except Exception as e:
            self.logger.error(f"コード実行エラー: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat()
            }
            self._record_execution(execution_id, code_info, error_result)
            return error_result
        
        finally:
            # 一時ファイルのクリーンアップ
            self._cleanup_temp_files(code_file_path)
    
    def _generate_execution_id(self) -> str:
        """実行IDを生成"""
        return f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _prepare_execution_environment(self) -> Dict[str, str]:
        """実行環境を準備"""
        env = os.environ.copy()
        
        # Pythonパスの設定
        env["PYTHONPATH"] = os.getcwd()
        
        # 出力ディレクトリの作成
        os.makedirs(config.OUTPUT_PATH, exist_ok=True)
        os.makedirs(config.DATA_PATH, exist_ok=True)
        
        return env
    
    def _create_code_file(self, code: str, execution_id: str) -> str:
        """コードファイルを作成"""
        # 実行用ディレクトリの作成
        execution_dir = os.path.join(config.EXECUTION_PATH, execution_id)
        os.makedirs(execution_dir, exist_ok=True)
        
        # コードファイルのパス
        code_file_path = os.path.join(execution_dir, f"{execution_id}.py")
        
        # セットアップコードの追加
        full_code = self._prepare_full_code(code)
        
        # ファイルに書き込み
        with open(code_file_path, 'w', encoding='utf-8') as f:
            f.write(full_code)
        
        self.logger.info(f"コードファイル作成: {code_file_path}")
        return code_file_path
    
    def _prepare_full_code(self, code: str) -> str:
        """実行用の完全なコードを準備"""
        setup_code = f"""
import sys
import os
import warnings

# 警告を抑制
warnings.filterwarnings('ignore')

# パスの設定
sys.path.append('{os.getcwd()}')
output_path = '{config.OUTPUT_PATH}'
data_path = '{config.DATA_PATH}'

# 出力ディレクトリの作成
os.makedirs(output_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)

# ファイルパスの置換
import re
code_text = '''{code}'''
code_text = code_text.replace('{{output_path}}', output_path)
code_text = code_text.replace('{{data_path}}', data_path)

print("=== 実行開始 ===")
"""
        
        execution_code = f"""
try:
    exec(code_text)
    print("=== 実行完了 ===")
except Exception as e:
    print(f"実行エラー: {{e}}")
    import traceback
    traceback.print_exc()
"""
        
        return setup_code + execution_code
    
    def _run_code(self, code_file_path: str, env: Dict[str, str]) -> Dict[str, Any]:
        """コードを実行"""
        start_time = datetime.now()
        
        try:
            # Pythonプロセスでコードを実行
            result = subprocess.run(
                [config.PYTHON_EXECUTABLE, code_file_path],
                capture_output=True,
                text=True,
                timeout=config.CODE_TIMEOUT,
                env=env,
                cwd=os.getcwd()
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"コード実行がタイムアウトしました: {config.CODE_TIMEOUT}秒")
            raise Exception(f"実行タイムアウト（{config.CODE_TIMEOUT}秒）")
        
        except Exception as e:
            self.logger.error(f"コード実行エラー: {e}")
            raise
    
    def _process_execution_result(self, result: Dict[str, Any], code_info: Dict[str, Any]) -> Dict[str, Any]:
        """実行結果を処理"""
        success = result["return_code"] == 0
        
        # 標準出力から重要な情報を抽出
        output_summary = self._extract_output_summary(result["stdout"])
        
        # 生成されたファイルの検索
        generated_files = self._find_generated_files()
        
        # エラー情報の処理
        error_info = None
        if not success:
            error_info = self._parse_error_output(result["stderr"])
        
        processed_result = {
            "success": success,
            "execution_time": result["execution_time"],
            "output_summary": output_summary,
            "generated_files": generated_files,
            "stdout": result["stdout"],
            "stderr": result["stderr"] if result["stderr"] else None,
            "error_info": error_info,
            "method_id": code_info["method_id"],
            "method_name": code_info["method_name"],
            "timestamp": datetime.now().isoformat()
        }
        
        return processed_result
    
    def _extract_output_summary(self, stdout: str) -> Dict[str, Any]:
        """標準出力から重要な情報を抽出"""
        summary = {
            "key_metrics": [],
            "data_info": {},
            "warnings": []
        }
        
        lines = stdout.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 重要な指標を抽出
            if any(keyword in line.lower() for keyword in ['r²', 'r2', 'rmse', 'シルエット', 'p値', 'p-value']):
                summary["key_metrics"].append(line)
            
            # データ情報を抽出
            elif 'データサイズ' in line or 'shape' in line:
                summary["data_info"]["size"] = line
            
            # 警告を抽出
            elif '警告' in line or 'warning' in line.lower():
                summary["warnings"].append(line)
        
        return summary
    
    def _find_generated_files(self) -> List[Dict[str, Any]]:
        """生成されたファイルを検索"""
        generated_files = []
        
        # 出力ディレクトリを検索
        if os.path.exists(config.OUTPUT_PATH):
            for root, dirs, files in os.walk(config.OUTPUT_PATH):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_info = {
                        "path": file_path,
                        "name": file,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        "type": self._get_file_type(file)
                    }
                    generated_files.append(file_info)
        
        return generated_files
    
    def _get_file_type(self, filename: str) -> str:
        """ファイルタイプを判定"""
        extension = os.path.splitext(filename)[1].lower()
        
        type_mapping = {
            ".csv": "data",
            ".json": "data", 
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".pdf": "document",
            ".txt": "text",
            ".html": "html"
        }
        
        return type_mapping.get(extension, "unknown")
    
    def _parse_error_output(self, stderr: str) -> Dict[str, Any]:
        """エラー出力を解析"""
        error_info = {
            "type": "unknown",
            "message": stderr,
            "suggestions": []
        }
        
        # 一般的なエラーパターンとその対処法
        error_patterns = {
            "ModuleNotFoundError": {
                "type": "missing_module",
                "suggestions": ["必要なライブラリをインストールしてください"]
            },
            "FileNotFoundError": {
                "type": "missing_file", 
                "suggestions": ["データファイルのパスを確認してください"]
            },
            "KeyError": {
                "type": "missing_column",
                "suggestions": ["指定された列名がデータに存在するか確認してください"]
            },
            "ValueError": {
                "type": "value_error",
                "suggestions": ["データの形式や値の範囲を確認してください"]
            }
        }
        
        for pattern, info in error_patterns.items():
            if pattern in stderr:
                error_info.update(info)
                break
        
        return error_info
    
    def _record_execution(self, execution_id: str, code_info: Dict[str, Any], result: Dict[str, Any]):
        """実行履歴を記録"""
        record = {
            "execution_id": execution_id,
            "method_id": code_info["method_id"],
            "method_name": code_info["method_name"],
            "success": result["success"],
            "execution_time": result.get("execution_time", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        self.execution_history.append(record)
        
        # 履歴ファイルに保存
        history_file = os.path.join(config.OUTPUT_PATH, "execution_history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.execution_history, f, ensure_ascii=False, indent=2)
    
    def _cleanup_temp_files(self, code_file_path: str):
        """一時ファイルをクリーンアップ"""
        try:
            if os.path.exists(code_file_path):
                os.remove(code_file_path)
                # 空のディレクトリも削除
                directory = os.path.dirname(code_file_path)
                if os.path.exists(directory) and not os.listdir(directory):
                    os.rmdir(directory)
        except Exception as e:
            self.logger.warning(f"一時ファイルの削除に失敗: {e}")
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """実行履歴を取得"""
        return self.execution_history
    
    def create_sample_data(self):
        """サンプルデータを作成（デモ用）"""
        import pandas as pd
        import numpy as np
        
        # サンプルデータの作成
        np.random.seed(42)
        n_samples = 1000
        
        sample_data = pd.DataFrame({
            '日付': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
            '売上': np.random.normal(1000, 200, n_samples),
            '顧客数': np.random.poisson(50, n_samples),
            'グループ': np.random.choice(['A', 'B'], n_samples),
            '地域': np.random.choice(['東京', '大阪', '名古屋'], n_samples)
        })
        
        # データファイルとして保存
        sample_file_path = os.path.join(config.DATA_PATH, "sample_data.csv")
        sample_data.to_csv(sample_file_path, index=False)
        
        self.logger.info(f"サンプルデータを作成しました: {sample_file_path}")
        return sample_file_path
