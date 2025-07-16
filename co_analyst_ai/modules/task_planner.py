"""
タスク分解・プランニングモジュール
複雑な分析リクエストを、RAGで取得した知識を考慮し、
実行可能な小さなステップに分解し、実行計画を生成
"""
import logging
from typing import Dict, List, Any, Optional

class TaskPlanner:
    """分析タスクを分解し実行計画を作成するクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_plan(self, parsed_intent: Dict[str, Any], relevant_knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        分析計画を作成
        
        Args:
            parsed_intent: 意図解釈の結果
            relevant_knowledge: RAG検索で取得した関連知識
            
        Returns:
            順序付けされた分析ステップのリスト
        """
        self.logger.info("分析計画作成開始")
        
        primary_intent = parsed_intent["intent"]["primary_intent"]
        analysis_type = parsed_intent["analysis_type"]
        
        # 基本的な分析フローを決定
        if primary_intent == "data_exploration":
            plan = self._create_exploration_plan(parsed_intent, relevant_knowledge)
        elif primary_intent == "descriptive_statistics":
            plan = self._create_descriptive_stats_plan(parsed_intent, relevant_knowledge)
        elif primary_intent == "correlation_analysis":
            plan = self._create_correlation_plan(parsed_intent, relevant_knowledge)
        elif primary_intent == "trend_analysis":
            plan = self._create_trend_analysis_plan(parsed_intent, relevant_knowledge)
        elif primary_intent == "clustering":
            plan = self._create_clustering_plan(parsed_intent, relevant_knowledge)
        elif primary_intent == "regression_analysis":
            plan = self._create_regression_plan(parsed_intent, relevant_knowledge)
        elif primary_intent == "hypothesis_testing":
            plan = self._create_hypothesis_testing_plan(parsed_intent, relevant_knowledge)
        else:
            # デフォルトで探索的分析
            plan = self._create_exploration_plan(parsed_intent, relevant_knowledge)
        
        # 計画の最適化と検証
        optimized_plan = self._optimize_plan(plan)
        
        self.logger.info(f"分析計画作成完了: {len(optimized_plan)}ステップ")
        return optimized_plan
    
    def _create_exploration_plan(self, parsed_intent: Dict[str, Any], knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """データ探索の計画を作成"""
        plan = [
            {
                "step_id": "1",
                "step_name": "データロードと基本情報確認",
                "task_description": "データファイルを読み込み、基本的な情報（行数、列数、データ型）を確認",
                "method_id": "data_load_info",
                "dependencies": [],
                "expected_output": "データの基本情報とサンプル"
            },
            {
                "step_id": "2", 
                "step_name": "記述統計量の計算",
                "task_description": "数値変数の記述統計量（平均、中央値、標準偏差等）を計算",
                "method_id": "desc_stats_summary",
                "dependencies": ["1"],
                "expected_output": "記述統計量テーブル"
            },
            {
                "step_id": "3",
                "step_name": "欠損値とデータ品質の確認",
                "task_description": "各列の欠損値の数と割合、データ品質を確認",
                "method_id": "data_quality_check",
                "dependencies": ["1"],
                "expected_output": "データ品質レポート"
            },
            {
                "step_id": "4",
                "step_name": "データ分布の可視化",
                "task_description": "主要な変数のヒストグラムや箱ひげ図を作成",
                "method_id": "distribution_visualization",
                "dependencies": ["2"],
                "expected_output": "分布グラフ"
            }
        ]
        return plan
    
    def _create_descriptive_stats_plan(self, parsed_intent: Dict[str, Any], knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """記述統計分析の計画を作成"""
        plan = [
            {
                "step_id": "1",
                "step_name": "データロード",
                "task_description": "データファイルを読み込み",
                "method_id": "data_load",
                "dependencies": [],
                "expected_output": "データフレーム"
            },
            {
                "step_id": "2",
                "step_name": "記述統計量計算",
                "task_description": "指定された変数の記述統計量を計算",
                "method_id": "desc_stats_summary",
                "dependencies": ["1"],
                "parameters": {
                    "variables": parsed_intent.get("extracted_variables", [])
                },
                "expected_output": "記述統計量テーブル"
            }
        ]
        
        # グループ化が指定されている場合
        if parsed_intent.get("groupby_variable"):
            plan.append({
                "step_id": "3",
                "step_name": "グループ別記述統計量",
                "task_description": "グループ別の記述統計量を計算",
                "method_id": "desc_stats_groupby",
                "dependencies": ["2"],
                "parameters": {
                    "groupby": parsed_intent["groupby_variable"]
                },
                "expected_output": "グループ別統計量テーブル"
            })
        
        return plan
    
    def _create_correlation_plan(self, parsed_intent: Dict[str, Any], knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """相関分析の計画を作成"""
        plan = [
            {
                "step_id": "1",
                "step_name": "データロード",
                "task_description": "データファイルを読み込み",
                "method_id": "data_load",
                "dependencies": [],
                "expected_output": "データフレーム"
            },
            {
                "step_id": "2",
                "step_name": "数値変数選択",
                "task_description": "相関分析対象の数値変数を選択",
                "method_id": "select_numeric_variables", 
                "dependencies": ["1"],
                "expected_output": "数値変数リスト"
            },
            {
                "step_id": "3",
                "step_name": "相関分析実行",
                "task_description": "変数間の相関係数を計算し、相関行列とヒートマップを作成",
                "method_id": "correlation_analysis",
                "dependencies": ["2"],
                "expected_output": "相関行列とヒートマップ"
            }
        ]
        return plan
    
    def _create_trend_analysis_plan(self, parsed_intent: Dict[str, Any], knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """トレンド分析の計画を作成"""
        plan = [
            {
                "step_id": "1",
                "step_name": "データロード",
                "task_description": "データファイルを読み込み",
                "method_id": "data_load",
                "dependencies": [],
                "expected_output": "データフレーム"
            },
            {
                "step_id": "2",
                "step_name": "日付列変換",
                "task_description": "日付データをdatetime型に変換",
                "method_id": "convert_to_datetime",
                "dependencies": ["1"],
                "parameters": {
                    "column": parsed_intent["entities"].get("date_columns", ["日付"])[0] if parsed_intent["entities"].get("date_columns") else "日付"
                },
                "expected_output": "日付変換済みデータ"
            },
            {
                "step_id": "3",
                "step_name": "時系列集計",
                "task_description": "指定された期間で数値データを集計",
                "method_id": "aggregate_by_month",
                "dependencies": ["2"],
                "parameters": {
                    "date_column": parsed_intent["entities"].get("date_columns", ["日付"])[0] if parsed_intent["entities"].get("date_columns") else "日付",
                    "value_column": parsed_intent["entities"].get("numeric_columns", ["売上"])[0] if parsed_intent["entities"].get("numeric_columns") else "売上"
                },
                "expected_output": "時系列集計データ"
            },
            {
                "step_id": "4",
                "step_name": "トレンド可視化",
                "task_description": "時系列データを折れ線グラフで可視化",
                "method_id": "line_chart",
                "dependencies": ["3"],
                "expected_output": "トレンドグラフ"
            }
        ]
        return plan
    
    def _create_clustering_plan(self, parsed_intent: Dict[str, Any], knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """クラスタリング分析の計画を作成"""
        plan = [
            {
                "step_id": "1",
                "step_name": "データロード",
                "task_description": "データファイルを読み込み",
                "method_id": "data_load",
                "dependencies": [],
                "expected_output": "データフレーム"
            },
            {
                "step_id": "2",
                "step_name": "特徴量選択",
                "task_description": "クラスタリングに使用する特徴量を選択",
                "method_id": "feature_selection",
                "dependencies": ["1"],
                "expected_output": "特徴量データ"
            },
            {
                "step_id": "3",
                "step_name": "欠損値処理",
                "task_description": "特徴量の欠損値を適切に処理",
                "method_id": "handle_missing_median",
                "dependencies": ["2"],
                "expected_output": "欠損値処理済みデータ"
            },
            {
                "step_id": "4",
                "step_name": "特徴量標準化",
                "task_description": "特徴量を標準化（平均0、分散1）",
                "method_id": "standardize_features",
                "dependencies": ["3"],
                "expected_output": "標準化済みデータ"
            },
            {
                "step_id": "5",
                "step_name": "K-meansクラスタリング実行",
                "task_description": "K-meansアルゴリズムでクラスタリングを実行",
                "method_id": "kmeans_clustering",
                "dependencies": ["4"],
                "parameters": {
                    "n_clusters": 4  # デフォルト値、後で調整可能
                },
                "expected_output": "クラスタリング結果"
            },
            {
                "step_id": "6",
                "step_name": "クラスター分析",
                "task_description": "各クラスターの特徴を分析",
                "method_id": "cluster_analysis",
                "dependencies": ["5"],
                "expected_output": "クラスター特徴分析"
            }
        ]
        return plan
    
    def _create_regression_plan(self, parsed_intent: Dict[str, Any], knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """回帰分析の計画を作成"""
        plan = [
            {
                "step_id": "1",
                "step_name": "データロード",
                "task_description": "データファイルを読み込み",
                "method_id": "data_load",
                "dependencies": [],
                "expected_output": "データフレーム"
            },
            {
                "step_id": "2",
                "step_name": "変数選択",
                "task_description": "目的変数と説明変数を選択",
                "method_id": "variable_selection",
                "dependencies": ["1"],
                "expected_output": "変数選択結果"
            },
            {
                "step_id": "3",
                "step_name": "前処理",
                "task_description": "欠損値処理と外れ値除去",
                "method_id": "data_preprocessing",
                "dependencies": ["2"],
                "expected_output": "前処理済みデータ"
            },
            {
                "step_id": "4",
                "step_name": "線形回帰分析",
                "task_description": "線形回帰モデルを構築し評価",
                "method_id": "linear_regression",
                "dependencies": ["3"],
                "expected_output": "回帰分析結果"
            }
        ]
        return plan
    
    def _create_hypothesis_testing_plan(self, parsed_intent: Dict[str, Any], knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """仮説検定の計画を作成"""
        plan = [
            {
                "step_id": "1",
                "step_name": "データロード",
                "task_description": "データファイルを読み込み",
                "method_id": "data_load",
                "dependencies": [],
                "expected_output": "データフレーム"
            },
            {
                "step_id": "2",
                "step_name": "検定対象変数の確認",
                "task_description": "検定対象の数値変数とグループ変数を確認",
                "method_id": "test_variable_check",
                "dependencies": ["1"],
                "expected_output": "検定変数情報"
            },
            {
                "step_id": "3",
                "step_name": "独立2標本t検定",
                "task_description": "2つのグループ間の平均値の差を検定",
                "method_id": "t_test_independent",
                "dependencies": ["2"],
                "expected_output": "t検定結果"
            }
        ]
        return plan
    
    def _optimize_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析計画を最適化"""
        # 依存関係の検証
        validated_plan = self._validate_dependencies(plan)
        
        # 重複ステップの除去
        deduplicated_plan = self._remove_duplicates(validated_plan)
        
        # 並列実行可能なステップの特定
        optimized_plan = self._identify_parallel_steps(deduplicated_plan)
        
        return optimized_plan
    
    def _validate_dependencies(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """依存関係を検証し、必要に応じて修正"""
        step_ids = [step["step_id"] for step in plan]
        
        for step in plan:
            for dep in step.get("dependencies", []):
                if dep not in step_ids:
                    self.logger.warning(f"無効な依存関係が検出されました: {step['step_id']} -> {dep}")
                    step["dependencies"].remove(dep)
        
        return plan
    
    def _remove_duplicates(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重複するステップを除去"""
        seen_methods = set()
        unique_plan = []
        
        for step in plan:
            method_id = step.get("method_id")
            if method_id not in seen_methods:
                seen_methods.add(method_id)
                unique_plan.append(step)
            else:
                self.logger.info(f"重複ステップを除去: {method_id}")
        
        return unique_plan
    
    def _identify_parallel_steps(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """並列実行可能なステップを特定"""
        # 現在の実装では順次実行
        # 将来的に並列実行のロジックを追加
        for i, step in enumerate(plan):
            step["execution_order"] = i + 1
            step["parallel_group"] = None  # 将来の並列実行用
        
        return plan
