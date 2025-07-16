"""
意図解釈・入力解析モジュール
ユーザーの自然言語入力から分析の目的、対象データ、制約条件を特定
"""
import re
import json
from typing import Dict, List, Any, Optional
import logging

class IntentParser:
    """ユーザー入力の意図を解釈するクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.intent_patterns = self._load_intent_patterns()
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """意図解釈用のパターンを定義"""
        return {
            "data_exploration": [
                r"データ.*探索", r"データ.*概要", r"データ.*確認", r"まず.*見", 
                r"どんな.*データ", r"データ.*理解"
            ],
            "descriptive_statistics": [
                r"記述統計", r"統計量", r"平均", r"中央値", r"標準偏差",
                r"基本.*統計", r"要約.*統計"
            ],
            "correlation_analysis": [
                r"相関", r"関係.*調", r"関連.*調", r"変数.*関係",
                r"どの.*関連", r"相関.*分析"
            ],
            "trend_analysis": [
                r"トレンド", r"推移", r"時系列", r"変化", r"傾向",
                r"売上.*推移", r"月別", r"年別"
            ],
            "clustering": [
                r"クラスタ", r"セグメント", r"グループ.*分", r"分類",
                r"顧客.*セグメント", r"クラスタリング"
            ],
            "regression_analysis": [
                r"回帰", r"予測", r"線形.*回帰", r"重回帰",
                r"予測.*モデル", r"関係.*モデル"
            ],
            "hypothesis_testing": [
                r"検定", r"有意.*差", r"t検定", r"仮説.*検定",
                r"差.*ある", r"統計.*検定"
            ],
            "visualization": [
                r"可視化", r"グラフ", r"チャート", r"プロット",
                r"グラフ.*作", r"可視化.*し"
            ]
        }
    
    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        ユーザー入力を解析し、構造化された分析リクエストを生成
        
        Args:
            user_input: ユーザーからの自然言語入力
            
        Returns:
            構造化された分析リクエスト
        """
        self.logger.info(f"意図解釈開始: {user_input}")
        
        # 基本的な意図分類
        intent = self._classify_intent(user_input)
        
        # エンティティ抽出
        entities = self._extract_entities(user_input)
        
        # データソース特定
        data_source = self._identify_data_source(user_input)
        
        # 制約条件抽出
        constraints = self._extract_constraints(user_input)
        
        # 優先度設定
        priority = self._determine_priority(user_input)
        
        result = {
            "intent": intent,
            "entities": entities,
            "data_source": data_source,
            "constraints": constraints,
            "priority": priority,
            "original_input": user_input,
            "extracted_variables": entities.get("variables", []),
            "target_variable": entities.get("target_variable"),
            "groupby_variable": entities.get("groupby_variable"),
            "analysis_type": intent["primary_intent"]
        }
        
        self.logger.info(f"意図解釈結果: {result}")
        return result
    
    def _classify_intent(self, text: str) -> Dict[str, Any]:
        """テキストから主要な意図を分類"""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            intent_scores[intent_type] = score
        
        # 最高スコアの意図を特定
        primary_intent = max(intent_scores, key=intent_scores.get) if max(intent_scores.values()) > 0 else "data_exploration"
        
        # 複数の意図が含まれる場合を考慮
        secondary_intents = [intent for intent, score in intent_scores.items() 
                           if score > 0 and intent != primary_intent]
        
        return {
            "primary_intent": primary_intent,
            "secondary_intents": secondary_intents,
            "confidence_scores": intent_scores
        }
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """テキストからエンティティ（変数名、ファイル名等）を抽出"""
        entities = {
            "variables": [],
            "file_names": [],
            "target_variable": None,
            "groupby_variable": None,
            "date_columns": [],
            "numeric_columns": []
        }
        
        # 一般的な変数名パターン
        variable_patterns = [
            r"[「『]([^」』]+)[」』]",  # 「変数名」形式
            r"[\'\"]([^\'\"]+)[\'\"]",  # 'variable_name' 形式
            r"([a-zA-Z_][a-zA-Z0-9_]*)",  # プログラミング変数名形式
        ]
        
        for pattern in variable_patterns:
            matches = re.findall(pattern, text)
            entities["variables"].extend(matches)
        
        # ファイル名パターン
        file_patterns = [
            r"([a-zA-Z0-9_\-\.]+\.csv)",
            r"([a-zA-Z0-9_\-\.]+\.xlsx?)",
            r"([a-zA-Z0-9_\-\.]+\.json)"
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, text)
            entities["file_names"].extend(matches)
        
        # 日付関連のキーワード
        date_keywords = ["日付", "date", "時間", "time", "年月", "年", "月"]
        for keyword in date_keywords:
            if keyword in text.lower():
                entities["date_columns"].append(keyword)
        
        # 数値関連のキーワード
        numeric_keywords = ["売上", "金額", "価格", "数量", "売上高", "revenue", "sales", "amount"]
        for keyword in numeric_keywords:
            if keyword in text.lower():
                entities["numeric_columns"].append(keyword)
        
        # 目的変数のヒント
        target_indicators = ["予測", "予想", "目的変数", "従属変数"]
        for indicator in target_indicators:
            if indicator in text:
                # より詳細な抽出ロジックが必要
                pass
        
        return entities
    
    def _identify_data_source(self, text: str) -> Dict[str, Any]:
        """データソースを特定"""
        data_source = {
            "type": "unknown",
            "location": None,
            "format": None
        }
        
        # ファイル形式の検出
        if ".csv" in text.lower():
            data_source["format"] = "csv"
        elif ".xlsx" in text.lower() or ".xls" in text.lower():
            data_source["format"] = "excel"
        elif ".json" in text.lower():
            data_source["format"] = "json"
        
        # データベース関連キーワード
        db_keywords = ["データベース", "database", "db", "sql"]
        if any(keyword in text.lower() for keyword in db_keywords):
            data_source["type"] = "database"
        
        # デフォルトでファイルベースと仮定
        if data_source["type"] == "unknown":
            data_source["type"] = "file"
        
        return data_source
    
    def _extract_constraints(self, text: str) -> List[Dict[str, Any]]:
        """制約条件を抽出"""
        constraints = []
        
        # 期間制約
        period_patterns = [
            r"([0-9]{4})年",
            r"([0-9]{1,2})月",
            r"最近.*([0-9]+).*月",
            r"過去.*([0-9]+).*年"
        ]
        
        for pattern in period_patterns:
            matches = re.findall(pattern, text)
            if matches:
                constraints.append({
                    "type": "period",
                    "values": matches
                })
        
        # 条件制約
        condition_patterns = [
            r"([^><=]+)[><=]+([^><=]+)",
            r"([^含除]+)を除く",
            r"([^含除]+)のみ"
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, text)
            if matches:
                constraints.append({
                    "type": "condition",
                    "values": matches
                })
        
        return constraints
    
    def _determine_priority(self, text: str) -> str:
        """分析の優先度を決定"""
        urgent_keywords = ["急ぎ", "至急", "すぐに", "早急"]
        if any(keyword in text for keyword in urgent_keywords):
            return "high"
        
        detailed_keywords = ["詳細", "詳しく", "丁寧", "しっかり"]
        if any(keyword in text for keyword in detailed_keywords):
            return "detailed"
        
        return "normal"
