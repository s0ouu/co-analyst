"""
コード生成モジュール
選択された手法とコードテンプレート、分析コンテキストに基づき、
具体的な分析コード（Python）を生成
"""
import logging
import re
from typing import Dict, List, Any, Optional
from config import config

class CodeGenerator:
    """分析コードを生成するクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate(self, step: Dict[str, Any], selected_method: Dict[str, Any]) -> Dict[str, Any]:
        """
        コードを生成
        
        Args:
            step: 実行するステップの詳細
            selected_method: 選択された手法の詳細
            
        Returns:
            生成されたコードとメタデータ
        """
        self.logger.info(f"コード生成開始: {selected_method['name']}")
        
        # コードテンプレートを取得
        template = selected_method.get("code_template", "")
        
        # パラメータを準備
        parameters = self._prepare_parameters(step, selected_method)
        
        # テンプレートに値を代入
        generated_code = self._substitute_template(template, parameters)
        
        # コード検証
        validated_code = self._validate_code(generated_code)
        
        result = {
            "code": validated_code,
            "language": "python",
            "method_id": selected_method["id"],
            "method_name": selected_method["name"],
            "library_dependencies": selected_method.get("library", ""),
            "parameters": parameters,
            "template_type": selected_method.get("template_type", "general")
        }
        
        self.logger.info(f"コード生成完了: {len(validated_code)}文字")
        return result
    
    def _prepare_parameters(self, step: Dict[str, Any], method: Dict[str, Any]) -> Dict[str, Any]:
        """テンプレートパラメータを準備"""
        parameters = {
            # 基本パス
            "data_path": self._get_data_path(),
            "output_path": config.OUTPUT_PATH,
            
            # デフォルト列名
            "date_column": "日付",
            "value_column": "売上", 
            "group_column": "グループ",
            "data_column": "値",
            "target_variable": "目的変数",
            "feature_variables": "['特徴量1', '特徴量2']",
            "features": "['特徴量1', '特徴量2']",
            "variables_select": "df.select_dtypes(include=[np.number]).columns.tolist()",
            "groupby_code": "",
            "variables_filter": "",
            "column": "列名",
            "columns": "['列1', '列2']",
            "x_axis": "x",
            "y_axis": "y", 
            "title": "グラフタイトル",
            "aggregation": "sum",
            "n_clusters": 4
        }
        
        # ステップのパラメータで上書き
        if "parameters" in step:
            parameters.update(step["parameters"])
        
        # 手法のパラメータで上書き
        if "parameters" in method:
            parameters.update(method["parameters"])
        
        # 手法固有の調整
        if "variables_filter" in method:
            parameters["variables_filter"] = method["variables_filter"]
        
        # リスト形式のパラメータを適切にフォーマット
        parameters = self._format_list_parameters(parameters)
        
        return parameters
    
    def _format_list_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """リスト形式のパラメータを適切にフォーマット"""
        list_params = ["feature_variables", "features", "columns"]
        
        for param in list_params:
            if param in parameters and isinstance(parameters[param], list):
                # リストを文字列形式に変換
                parameters[param] = str(parameters[param])
        
        return parameters
    
    def _substitute_template(self, template: str, parameters: Dict[str, Any]) -> str:
        """テンプレートに値を代入"""
        code = template
        
        # パラメータを順次置換
        for key, value in parameters.items():
            placeholder = "{" + key + "}"
            if placeholder in code:
                code = code.replace(placeholder, str(value))
        
        # 残った未定義のプレースホルダーを処理
        code = self._handle_undefined_placeholders(code)
        
        return code
    
    def _handle_undefined_placeholders(self, code: str) -> str:
        """未定義のプレースホルダーを処理"""
        # 未定義のプレースホルダーパターンを検索
        undefined_pattern = r'\{([^}]+)\}'
        matches = re.findall(undefined_pattern, code)
        
        for match in matches:
            placeholder = "{" + match + "}"
            # デフォルト値で置換
            default_value = self._get_default_value(match)
            code = code.replace(placeholder, default_value)
            self.logger.warning(f"未定義のプレースホルダーをデフォルト値で置換: {match} -> {default_value}")
        
        return code
    
    def _get_default_value(self, parameter_name: str) -> str:
        """パラメータのデフォルト値を取得"""
        defaults = {
            "data_path": "data/sample_data.csv",
            "output_path": config.OUTPUT_PATH,
            "column": "column_name",
            "columns": "['column1', 'column2']",
            "date_column": "日付",
            "value_column": "値",
            "group_column": "グループ",
            "data_column": "データ",
            "target_variable": "target",
            "feature_variables": "['feature1', 'feature2']",
            "features": "['feature1', 'feature2']",
            "x_axis": "x",
            "y_axis": "y",
            "title": "分析結果",
            "aggregation": "sum",
            "n_clusters": "4"
        }
        return defaults.get(parameter_name, f"'{parameter_name}'")
    
    def _validate_code(self, code: str) -> str:
        """生成されたコードを検証"""
        # 基本的な構文チェック
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            self.logger.error(f"構文エラーが検出されました: {e}")
            # エラー修正の試行
            code = self._fix_syntax_errors(code)
        
        # 安全性チェック
        code = self._security_check(code)
        
        return code
    
    def _fix_syntax_errors(self, code: str) -> str:
        """構文エラーの修正を試行"""
        # よくある構文エラーの修正
        fixes = [
            # クォートの修正
            (r"df\['([^']+)'\]\.isnull\(\)\.sum\(\)", r"df['\1'].isnull().sum()"),
            # インデントの修正
            (r"^(\s*)(print\()", r"\1\2"),
        ]
        
        for pattern, replacement in fixes:
            code = re.sub(pattern, replacement, code, flags=re.MULTILINE)
        
        return code
    
    def _security_check(self, code: str) -> str:
        """セキュリティチェック"""
        # 危険な操作をチェック
        dangerous_patterns = [
            r"import\s+os",
            r"exec\s*\(",
            r"eval\s*\(",
            r"__import__",
            r"open\s*\(.+[\"']w[\"']",  # ファイル書き込み（許可されたパス以外）
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                self.logger.warning(f"潜在的に危険な操作が検出されました: {pattern}")
        
        return code
    
    def _get_data_path(self) -> str:
        """データファイルのパスを取得"""
        # 実際の実装では、ユーザーが指定したファイルパスを使用
        # ここではデモ用のサンプルパス
        return f"{config.DATA_PATH}/sample_data.csv"
    
    def generate_setup_code(self) -> str:
        """分析前の基本セットアップコードを生成"""
        setup_code = """
# 基本ライブラリのインポート
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings

# 警告を非表示
warnings.filterwarnings('ignore')

# matplotlibの設定
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12

# 出力ディレクトリの作成
import os
os.makedirs('outputs', exist_ok=True)

print("セットアップ完了")
"""
        return setup_code.strip()
    
    def generate_cleanup_code(self) -> str:
        """分析後のクリーンアップコードを生成"""
        cleanup_code = """
# メモリの解放
import gc
gc.collect()

# matplotlibのクリーンアップ
plt.close('all')

print("分析完了")
"""
        return cleanup_code.strip()
