"""
応答生成モジュール
これまでの分析プロセス（意図、実行ステップ、結果、解釈）を統合し、
ユーザーへの最終的な対話応答として整形
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class ResponseGenerator:
    """ユーザーへの応答を生成するクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate(self, 
                user_input: str, 
                parsed_intent: Dict[str, Any], 
                execution_results: List[Dict[str, Any]], 
                interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """
        最終的なユーザー応答を生成
        
        Args:
            user_input: 元のユーザー入力
            parsed_intent: 意図解釈結果
            execution_results: 実行結果
            interpretation: 解釈結果
            
        Returns:
            ユーザー向け応答
        """
        self.logger.info("応答生成開始")
        
        # 応答の基本構造を作成
        response = {
            "greeting": self._generate_greeting(parsed_intent),
            "analysis_summary": self._generate_analysis_summary(execution_results),
            "key_findings": self._generate_key_findings(interpretation),
            "detailed_results": self._generate_detailed_results(execution_results, interpretation),
            "visualizations": self._generate_visualization_info(execution_results),
            "recommendations": self._generate_recommendations(interpretation),
            "next_steps": self._generate_next_steps(parsed_intent, execution_results),
            "technical_details": self._generate_technical_details(execution_results),
            "session_info": {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": parsed_intent.get("analysis_type", "unknown"),
                "steps_completed": len([r for r in execution_results if r["success"]]),
                "total_steps": len(execution_results)
            }
        }
        
        # 応答のトーンを調整
        response = self._adjust_response_tone(response, parsed_intent)
        
        # 最終的な応答テキストを構築
        response["formatted_response"] = self._format_final_response(response)
        
        self.logger.info("応答生成完了")
        return response
    
    def _generate_greeting(self, parsed_intent: Dict[str, Any]) -> str:
        """挨拶とコンテキストの確認"""
        analysis_type = parsed_intent.get("analysis_type", "分析")
        
        greeting_templates = {
            "data_exploration": "データの探索分析を実行しました。",
            "descriptive_statistics": "記述統計分析を実行しました。",
            "correlation_analysis": "相関分析を実行しました。",
            "trend_analysis": "トレンド分析を実行しました。",
            "clustering": "クラスタリング分析を実行しました。",
            "regression_analysis": "回帰分析を実行しました。",
            "hypothesis_testing": "仮説検定を実行しました。"
        }
        
        return greeting_templates.get(analysis_type, f"{analysis_type}を実行しました。")
    
    def _generate_analysis_summary(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析の概要を生成"""
        successful_steps = [r for r in execution_results if r["success"]]
        failed_steps = [r for r in execution_results if not r["success"]]
        
        total_time = sum(r.get("execution_time", 0) for r in execution_results)
        
        summary = {
            "total_steps": len(execution_results),
            "successful_steps": len(successful_steps),
            "failed_steps": len(failed_steps),
            "total_execution_time": f"{total_time:.2f}秒",
            "success_rate": f"{len(successful_steps)/len(execution_results)*100:.1f}%" if execution_results else "0%",
            "status": "完了" if len(failed_steps) == 0 else "部分完了" if len(successful_steps) > 0 else "失敗"
        }
        
        return summary
    
    def _generate_key_findings(self, interpretation: Dict[str, Any]) -> List[str]:
        """主要な発見を生成"""
        key_insights = interpretation.get("key_insights", [])
        
        if not key_insights:
            # 個別解釈から重要なポイントを抽出
            individual_interpretations = interpretation.get("individual_interpretations", [])
            key_insights = []
            
            for interp in individual_interpretations:
                interpretation_data = interp.get("interpretation", {})
                if "summary" in interpretation_data:
                    key_insights.append(interpretation_data["summary"])
        
        return key_insights[:3]  # 上位3つまで
    
    def _generate_detailed_results(self, execution_results: List[Dict[str, Any]], interpretation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """詳細結果を生成"""
        detailed_results = []
        individual_interpretations = interpretation.get("individual_interpretations", [])
        
        for i, result in enumerate(execution_results):
            if result["success"]:
                # 対応する解釈を検索
                corresponding_interpretation = None
                if i < len(individual_interpretations):
                    corresponding_interpretation = individual_interpretations[i]
                
                detail = {
                    "step_name": result.get("method_name", "Unknown"),
                    "status": "成功",
                    "execution_time": f"{result.get('execution_time', 0):.2f}秒",
                    "generated_files": [f["name"] for f in result.get("generated_files", [])],
                    "interpretation": corresponding_interpretation.get("interpretation", {}).get("summary", "") if corresponding_interpretation else "",
                    "key_metrics": self._extract_key_metrics(result)
                }
            else:
                detail = {
                    "step_name": result.get("method_name", "Unknown"),
                    "status": "失敗",
                    "error_message": result.get("error_info", {}).get("message", ""),
                    "suggestions": result.get("error_info", {}).get("suggestions", [])
                }
            
            detailed_results.append(detail)
        
        return detailed_results
    
    def _extract_key_metrics(self, result: Dict[str, Any]) -> List[str]:
        """実行結果から重要な指標を抽出"""
        metrics = []
        output_summary = result.get("output_summary", {})
        
        if "key_metrics" in output_summary:
            metrics.extend(output_summary["key_metrics"])
        
        return metrics
    
    def _generate_visualization_info(self, execution_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """可視化情報を生成"""
        visualizations = []
        
        for result in execution_results:
            if result["success"]:
                generated_files = result.get("generated_files", [])
                for file_info in generated_files:
                    if file_info.get("type") == "image":
                        viz_info = {
                            "title": self._generate_visualization_title(file_info["name"], result),
                            "file_path": file_info["path"],
                            "file_name": file_info["name"],
                            "description": self._generate_visualization_description(file_info["name"])
                        }
                        visualizations.append(viz_info)
        
        return visualizations
    
    def _generate_visualization_title(self, filename: str, result: Dict[str, Any]) -> str:
        """可視化のタイトルを生成"""
        method_name = result.get("method_name", "")
        
        title_mapping = {
            "correlation_heatmap.png": "変数間相関ヒートマップ",
            "clustering_plot.png": "クラスタリング結果",
            "regression_plot.png": "回帰分析結果",
            "line_chart.png": "トレンドグラフ"
        }
        
        return title_mapping.get(filename, f"{method_name}の結果")
    
    def _generate_visualization_description(self, filename: str) -> str:
        """可視化の説明を生成"""
        descriptions = {
            "correlation_heatmap.png": "変数間の相関の強さを色で表現したヒートマップです。濃い色ほど強い相関を示します。",
            "clustering_plot.png": "各データポイントがどのクラスターに属するかを色分けして表示しています。",
            "regression_plot.png": "実測値と予測値の関係、および回帰直線を示しています。",
            "line_chart.png": "時系列データの変化を折れ線グラフで表現しています。"
        }
        
        return descriptions.get(filename, "分析結果の可視化です。")
    
    def _generate_recommendations(self, interpretation: Dict[str, Any]) -> List[str]:
        """推奨事項を生成"""
        recommendations = interpretation.get("recommendations", [])
        
        if not recommendations:
            # デフォルトの推奨事項
            recommendations = [
                "分析結果をビジネス戦略に活用することを検討してください。",
                "必要に応じて追加の分析や異なる手法を試してください。"
            ]
        
        return recommendations
    
    def _generate_next_steps(self, parsed_intent: Dict[str, Any], execution_results: List[Dict[str, Any]]) -> List[str]:
        """次のステップを提案"""
        next_steps = []
        
        analysis_type = parsed_intent.get("analysis_type", "")
        successful_results = [r for r in execution_results if r["success"]]
        
        # 分析タイプに基づく提案
        if analysis_type == "data_exploration":
            next_steps.extend([
                "特定の変数について詳細な分析を実施する",
                "相関分析や回帰分析を実行する",
                "データの可視化を追加する"
            ])
        elif analysis_type == "correlation_analysis":
            next_steps.extend([
                "強い相関が見つかった変数ペアについて因果関係を調査する",
                "回帰分析で予測モデルを構築する"
            ])
        elif analysis_type == "clustering":
            next_steps.extend([
                "各クラスターの詳細な特徴を分析する",
                "クラスター別の戦略を策定する",
                "新しいデータポイントのクラスター予測を実装する"
            ])
        
        # 実行結果に基づく提案
        if len(successful_results) > 0:
            next_steps.append("結果をレポートとしてまとめる")
        
        return next_steps[:5]  # 上位5つまで
    
    def _generate_technical_details(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """技術的詳細を生成"""
        methods_used = []
        libraries_used = set()
        
        for result in execution_results:
            if result["success"]:
                methods_used.append(result.get("method_name", "Unknown"))
                # ライブラリ情報があれば追加
                if "library_dependencies" in result:
                    libs = result["library_dependencies"].split(", ")
                    libraries_used.update(libs)
        
        return {
            "methods_used": methods_used,
            "libraries_used": list(libraries_used),
            "total_files_generated": sum(len(r.get("generated_files", [])) for r in execution_results)
        }
    
    def _adjust_response_tone(self, response: Dict[str, Any], parsed_intent: Dict[str, Any]) -> Dict[str, Any]:
        """応答のトーンを調整"""
        priority = parsed_intent.get("priority", "normal")
        
        if priority == "detailed":
            # 詳細な説明を追加
            response["additional_details"] = "詳細な分析結果と解釈を提供しています。"
        elif priority == "high":
            # 簡潔で要点を押さえた応答
            response["urgency_note"] = "重要な結果を優先的に表示しています。"
        
        return response
    
    def _format_final_response(self, response: Dict[str, Any]) -> str:
        """最終的な応答テキストをフォーマット"""
        formatted_parts = []
        
        # 挨拶
        formatted_parts.append(response["greeting"])
        
        # 分析概要
        summary = response["analysis_summary"]
        formatted_parts.append(f"\n📊 **分析概要**")
        formatted_parts.append(f"- ステータス: {summary['status']}")
        formatted_parts.append(f"- 実行ステップ: {summary['successful_steps']}/{summary['total_steps']} 成功")
        formatted_parts.append(f"- 実行時間: {summary['total_execution_time']}")
        
        # 主要な発見
        key_findings = response["key_findings"]
        if key_findings:
            formatted_parts.append(f"\n🔍 **主要な発見**")
            for i, finding in enumerate(key_findings, 1):
                formatted_parts.append(f"{i}. {finding}")
        
        # 可視化
        visualizations = response["visualizations"]
        if visualizations:
            formatted_parts.append(f"\n📈 **生成された可視化**")
            for viz in visualizations:
                formatted_parts.append(f"- {viz['title']}: {viz['file_name']}")
        
        # 推奨事項
        recommendations = response["recommendations"]
        if recommendations:
            formatted_parts.append(f"\n💡 **推奨事項**")
            for i, rec in enumerate(recommendations, 1):
                formatted_parts.append(f"{i}. {rec}")
        
        # 次のステップ
        next_steps = response["next_steps"]
        if next_steps:
            formatted_parts.append(f"\n➡️ **次のステップ提案**")
            for i, step in enumerate(next_steps, 1):
                formatted_parts.append(f"{i}. {step}")
        
        # 技術的詳細（簡略版）
        tech_details = response["technical_details"]
        formatted_parts.append(f"\n🔧 **技術詳細**")
        formatted_parts.append(f"- 使用手法: {', '.join(tech_details['methods_used'])}")
        formatted_parts.append(f"- 生成ファイル: {tech_details['total_files_generated']}個")
        
        # 追加質問の促進
        formatted_parts.append(f"\n❓ **ご質問やさらなる分析をご希望でしたら、お聞かせください。**")
        
        return "\n".join(formatted_parts)
