"""
RAG検索モジュール
意図解釈の結果に基づき、外部JSONファイル群から関連する分析手法、
データ加工方法、解釈ガイドライン、分析例などを検索・取得
"""
import json
import os
from typing import Dict, List, Any, Optional
import logging
from config import config

class RAGSearcher:
    """RAG（Retrieval-Augmented Generation）検索を行うクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """知識ベースファイルを読み込み"""
        knowledge_base = {}
        
        # 分析手法
        try:
            with open(os.path.join(config.KNOWLEDGE_BASE_PATH, "analysis_methods.json"), 'r', encoding='utf-8') as f:
                knowledge_base["analysis_methods"] = json.load(f)
        except FileNotFoundError:
            self.logger.warning("analysis_methods.json not found")
            knowledge_base["analysis_methods"] = []
        
        # データ処理方法
        try:
            with open(os.path.join(config.KNOWLEDGE_BASE_PATH, "data_processing.json"), 'r', encoding='utf-8') as f:
                knowledge_base["data_processing"] = json.load(f)
        except FileNotFoundError:
            self.logger.warning("data_processing.json not found")
            knowledge_base["data_processing"] = []
        
        # 解釈ガイドライン
        try:
            with open(os.path.join(config.KNOWLEDGE_BASE_PATH, "interpretation_guidelines.json"), 'r', encoding='utf-8') as f:
                knowledge_base["interpretation_guidelines"] = json.load(f)
        except FileNotFoundError:
            self.logger.warning("interpretation_guidelines.json not found")
            knowledge_base["interpretation_guidelines"] = []
        
        # 分析例
        try:
            with open(os.path.join(config.KNOWLEDGE_BASE_PATH, "analysis_examples.json"), 'r', encoding='utf-8') as f:
                knowledge_base["analysis_examples"] = json.load(f)
        except FileNotFoundError:
            self.logger.warning("analysis_examples.json not found")
            knowledge_base["analysis_examples"] = []
        
        self.logger.info("知識ベース読み込み完了")
        return knowledge_base
    
    def search(self, parsed_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析された意図に基づいて関連知識を検索
        
        Args:
            parsed_intent: 意図解釈の結果
            
        Returns:
            関連する知識ベースの情報
        """
        self.logger.info(f"RAG検索開始: {parsed_intent['intent']['primary_intent']}")
        
        primary_intent = parsed_intent["intent"]["primary_intent"]
        secondary_intents = parsed_intent["intent"]["secondary_intents"]
        
        # 各カテゴリから関連情報を検索
        relevant_methods = self._search_analysis_methods(primary_intent, secondary_intents)
        relevant_processing = self._search_data_processing(parsed_intent)
        relevant_guidelines = self._search_interpretation_guidelines(relevant_methods)
        relevant_examples = self._search_analysis_examples(primary_intent)
        
        result = {
            "analysis_methods": relevant_methods,
            "data_processing": relevant_processing,
            "interpretation_guidelines": relevant_guidelines,
            "analysis_examples": relevant_examples,
            "search_summary": {
                "primary_intent": primary_intent,
                "methods_found": len(relevant_methods),
                "processing_found": len(relevant_processing),
                "guidelines_found": len(relevant_guidelines),
                "examples_found": len(relevant_examples)
            }
        }
        
        self.logger.info(f"RAG検索完了: {result['search_summary']}")
        return result
    
    def _search_analysis_methods(self, primary_intent: str, secondary_intents: List[str]) -> List[Dict[str, Any]]:
        """分析手法を検索"""
        relevant_methods = []
        
        # 意図に基づくマッピング
        intent_to_methods = {
            "data_exploration": ["desc_stats_summary"],
            "descriptive_statistics": ["desc_stats_summary"],
            "correlation_analysis": ["correlation_analysis"],
            "trend_analysis": ["desc_stats_summary", "linear_regression"],
            "clustering": ["kmeans_clustering"],
            "regression_analysis": ["linear_regression"],
            "hypothesis_testing": ["t_test_independent"],
            "visualization": ["correlation_analysis"]
        }
        
        # 主要意図に対応する手法を取得
        target_method_ids = intent_to_methods.get(primary_intent, [])
        
        # 副次的意図も考慮
        for intent in secondary_intents:
            target_method_ids.extend(intent_to_methods.get(intent, []))
        
        # 重複除去
        target_method_ids = list(set(target_method_ids))
        
        # 該当する手法を知識ベースから検索
        for method in self.knowledge_base.get("analysis_methods", []):
            if method["id"] in target_method_ids:
                relevant_methods.append(method)
            # タグでも検索
            elif any(tag in method.get("tags", []) for tag in self._intent_to_tags(primary_intent)):
                relevant_methods.append(method)
        
        return relevant_methods
    
    def _search_data_processing(self, parsed_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """データ処理方法を検索"""
        relevant_processing = []
        
        # 必要な前処理ステップを推定
        needed_processing = []
        
        # 意図に基づく前処理の推定
        intent = parsed_intent["intent"]["primary_intent"]
        entities = parsed_intent["entities"]
        
        # 日付関連の処理が必要か
        if entities.get("date_columns") or intent == "trend_analysis":
            needed_processing.extend(["convert_to_datetime", "aggregate_by_month"])
        
        # 数値データの前処理
        if intent in ["clustering", "regression_analysis"]:
            needed_processing.extend(["handle_missing_median", "standardize_features"])
        
        # 外れ値処理
        if intent in ["clustering", "regression_analysis", "correlation_analysis"]:
            needed_processing.append("remove_outliers_iqr")
        
        # カテゴリカルデータの処理
        if intent == "regression_analysis":
            needed_processing.append("create_dummy_variables")
        
        # 該当する処理方法を知識ベースから検索
        for processing in self.knowledge_base.get("data_processing", []):
            if processing["id"] in needed_processing:
                relevant_processing.append(processing)
        
        return relevant_processing
    
    def _search_interpretation_guidelines(self, relevant_methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解釈ガイドラインを検索"""
        relevant_guidelines = []
        
        # 分析手法に関連するガイドラインIDを取得
        guideline_ids = []
        for method in relevant_methods:
            guideline_id = method.get("interpretation_guideline_id")
            if guideline_id:
                guideline_ids.append(guideline_id)
        
        # 該当するガイドラインを検索
        for guideline in self.knowledge_base.get("interpretation_guidelines", []):
            if guideline["id"] in guideline_ids:
                relevant_guidelines.append(guideline)
        
        return relevant_guidelines
    
    def _search_analysis_examples(self, primary_intent: str) -> List[Dict[str, Any]]:
        """分析例を検索"""
        relevant_examples = []
        
        # 意図に基づく例の検索
        intent_to_example_ids = {
            "trend_analysis": ["sales_trend_analysis"],
            "clustering": ["customer_segmentation"],
            "correlation_analysis": ["correlation_analysis_example"],
            "data_exploration": ["data_exploration"]
        }
        
        target_example_ids = intent_to_example_ids.get(primary_intent, [])
        
        # 該当する例を検索
        for example in self.knowledge_base.get("analysis_examples", []):
            if example["id"] in target_example_ids:
                relevant_examples.append(example)
        
        return relevant_examples
    
    def _intent_to_tags(self, intent: str) -> List[str]:
        """意図をタグに変換"""
        intent_tag_mapping = {
            "data_exploration": ["データ探索"],
            "descriptive_statistics": ["記述統計"],
            "correlation_analysis": ["相関分析"],
            "trend_analysis": ["時系列"],
            "clustering": ["クラスタリング", "機械学習"],
            "regression_analysis": ["回帰分析", "機械学習"],
            "hypothesis_testing": ["推測統計", "仮説検定"],
            "visualization": ["可視化"]
        }
        return intent_tag_mapping.get(intent, [])
    
    def get_method_by_id(self, method_id: str) -> Optional[Dict[str, Any]]:
        """IDによる特定の手法の取得"""
        for method in self.knowledge_base.get("analysis_methods", []):
            if method["id"] == method_id:
                return method
        return None
    
    def get_processing_by_id(self, processing_id: str) -> Optional[Dict[str, Any]]:
        """IDによる特定の処理方法の取得"""
        for processing in self.knowledge_base.get("data_processing", []):
            if processing["id"] == processing_id:
                return processing
        return None
    
    def get_guideline_by_id(self, guideline_id: str) -> Optional[Dict[str, Any]]:
        """IDによる特定のガイドラインの取得"""
        for guideline in self.knowledge_base.get("interpretation_guidelines", []):
            if guideline["id"] == guideline_id:
                return guideline
        return None
