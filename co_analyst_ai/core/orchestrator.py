"""
Co-Analyst AI メインオーケストレーター
システム全体の中心となり、ユーザーからの指示を受けて各モジュールを連携させる
"""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import config
from modules.intent_parser import IntentParser
from modules.rag_searcher import RAGSearcher
from modules.task_planner import TaskPlanner
from modules.method_selector import MethodSelector
from modules.code_generator import CodeGenerator
from modules.result_interpreter import ResultInterpreter
from modules.response_generator import ResponseGenerator
from execution.code_executor import CodeExecutor

class CoAnalystOrchestrator:
    """
    Co-Analyst AIのメインオーケストレーター
    """
    
    def __init__(self):
        """初期化"""
        self.setup_logging()
        self.session_state = {}
        self.analysis_history = []
        
        # 各モジュールの初期化
        self.intent_parser = IntentParser()
        self.rag_searcher = RAGSearcher()
        self.task_planner = TaskPlanner()
        self.method_selector = MethodSelector()
        self.code_generator = CodeGenerator()
        self.result_interpreter = ResultInterpreter()
        self.response_generator = ResponseGenerator()
        self.code_executor = CodeExecutor()
        
        self.logger.info("Co-Analyst AIオーケストレーター初期化完了")
    
    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def start_session(self, session_id: str = None) -> str:
        """新しい分析セッションを開始"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.session_state[session_id] = {
            "created_at": datetime.now(),
            "current_step": 0,
            "analysis_plan": [],
            "execution_results": [],
            "context": {}
        }
        
        self.logger.info(f"新しい分析セッション開始: {session_id}")
        return session_id
    
    def process_user_input(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """
        ユーザー入力を処理し、分析結果を返す
        
        Args:
            user_input: ユーザーからの自然言語入力
            session_id: セッションID
            
        Returns:
            分析結果と応答
        """
        try:
            self.logger.info(f"ユーザー入力処理開始: {user_input[:50]}...")
            
            # 1. 意図解釈・入力解析
            parsed_intent = self.intent_parser.parse(user_input)
            self.logger.info(f"意図解釈結果: {parsed_intent}")
            
            # 2. 知識検索 (RAG)
            relevant_knowledge = self.rag_searcher.search(parsed_intent)
            self.logger.info(f"関連知識取得: {len(relevant_knowledge)}件")
            
            # 3. タスク分解・プランニング
            analysis_plan = self.task_planner.create_plan(parsed_intent, relevant_knowledge)
            self.logger.info(f"分析計画作成: {len(analysis_plan)}ステップ")
            
            # セッション状態更新
            self.session_state[session_id]["analysis_plan"] = analysis_plan
            self.session_state[session_id]["context"].update(parsed_intent)
            
            # 4. 各ステップの実行
            execution_results = []
            for step in analysis_plan:
                try:
                    result = self.execute_analysis_step(step, session_id)
                    execution_results.append(result)
                    self.session_state[session_id]["execution_results"].append(result)
                except Exception as e:
                    self.logger.error(f"ステップ実行エラー: {e}")
                    execution_results.append({
                        "step_id": step.get("step_id", "unknown"),
                        "status": "error",
                        "error": str(e)
                    })
            
            # 5. 結果解釈
            interpretation = self.result_interpreter.interpret(execution_results, relevant_knowledge)
            
            # 6. 応答生成
            response = self.response_generator.generate(
                user_input, parsed_intent, execution_results, interpretation
            )
            
            # 分析履歴に追加
            self.analysis_history.append({
                "timestamp": datetime.now(),
                "user_input": user_input,
                "session_id": session_id,
                "response": response
            })
            
            return {
                "status": "success",
                "session_id": session_id,
                "response": response,
                "execution_results": execution_results,
                "interpretation": interpretation
            }
            
        except Exception as e:
            self.logger.error(f"ユーザー入力処理エラー: {e}")
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id
            }
    
    def execute_analysis_step(self, step: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        個別の分析ステップを実行
        
        Args:
            step: 実行するステップの詳細
            session_id: セッションID
            
        Returns:
            ステップの実行結果
        """
        self.logger.info(f"ステップ実行開始: {step.get('task_description', 'Unknown')}")
        
        # 手法・ツール選択
        selected_method = self.method_selector.select(step)
        
        # コード生成
        generated_code = self.code_generator.generate(step, selected_method)
        
        # コード実行
        execution_result = self.code_executor.execute(generated_code)
        
        return {
            "step_id": step.get("step_id"),
            "task_description": step.get("task_description"),
            "method": selected_method,
            "code": generated_code,
            "execution_result": execution_result,
            "status": "completed" if execution_result.get("success") else "failed"
        }
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """セッション状態を取得"""
        return self.session_state.get(session_id, {})
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """分析履歴を取得"""
        return self.analysis_history
