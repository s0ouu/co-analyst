"""
結果解釈・説明モジュール
コード実行環境から得られた分析結果を、RAGで取得した解釈ガイドラインや
分析例を参照して、ユーザーにとって分かりやすい言葉で解釈し、説明を生成
"""
import json
import logging
import re
from typing import Dict, List, Any, Optional

class ResultInterpreter:
    """分析結果を解釈するクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def interpret(self, execution_results: List[Dict[str, Any]], relevant_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析結果を解釈
        
        Args:
            execution_results: 各ステップの実行結果
            relevant_knowledge: RAG検索で取得した関連知識
            
        Returns:
            解釈結果
        """
        self.logger.info("結果解釈開始")
        
        interpretations = []
        
        for result in execution_results:
            if result["success"]:
                interpretation = self._interpret_single_result(result, relevant_knowledge)
                interpretations.append(interpretation)
            else:
                # エラーの場合の解釈
                error_interpretation = self._interpret_error(result)
                interpretations.append(error_interpretation)
        
        # 全体的な解釈の統合
        overall_interpretation = self._create_overall_interpretation(interpretations)
        
        interpretation_result = {
            "individual_interpretations": interpretations,
            "overall_interpretation": overall_interpretation,
            "key_insights": self._extract_key_insights(interpretations),
            "recommendations": self._generate_recommendations(interpretations),
            "data_quality_assessment": self._assess_data_quality(execution_results)
        }
        
        self.logger.info("結果解釈完了")
        return interpretation_result
    
    def _interpret_single_result(self, result: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """単一の実行結果を解釈"""
        method_id = result.get("method_id", "unknown")
        
        # 手法に応じた解釈
        if method_id == "desc_stats_summary":
            interpretation = self._interpret_descriptive_stats(result, knowledge)
        elif method_id == "correlation_analysis":
            interpretation = self._interpret_correlation(result, knowledge)
        elif method_id == "t_test_independent":
            interpretation = self._interpret_t_test(result, knowledge)
        elif method_id == "linear_regression":
            interpretation = self._interpret_regression(result, knowledge)
        elif method_id == "kmeans_clustering":
            interpretation = self._interpret_clustering(result, knowledge)
        else:
            interpretation = self._interpret_general(result, knowledge)
        
        return {
            "method_id": method_id,
            "method_name": result.get("method_name", "Unknown"),
            "interpretation": interpretation,
            "confidence": self._assess_interpretation_confidence(result, interpretation)
        }
    
    def _interpret_descriptive_stats(self, result: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """記述統計量の解釈"""
        output = result.get("stdout", "")
        
        # 数値を抽出
        stats_values = self._extract_statistics_from_output(output)
        
        interpretation = {
            "summary": "データの基本的な統計情報を分析しました。",
            "findings": [],
            "data_characteristics": []
        }
        
        # 分布の特徴を分析
        if stats_values:
            for var, stats in stats_values.items():
                finding = f"{var}の平均値は{stats.get('mean', 'N/A')}、標準偏差は{stats.get('std', 'N/A')}です。"
                interpretation["findings"].append(finding)
                
                # 分布の偏りを判定
                mean = stats.get('mean')
                median = stats.get('50%')  # 中央値
                if mean and median:
                    try:
                        mean_val = float(mean)
                        median_val = float(median)
                        if abs(mean_val - median_val) / median_val > 0.1:
                            if mean_val > median_val:
                                interpretation["data_characteristics"].append(f"{var}は右に偏った分布を示しています。")
                            else:
                                interpretation["data_characteristics"].append(f"{var}は左に偏った分布を示しています。")
                        else:
                            interpretation["data_characteristics"].append(f"{var}は比較的対称的な分布を示しています。")
                    except (ValueError, TypeError):
                        pass
        
        return interpretation
    
    def _interpret_correlation(self, result: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """相関分析の解釈"""
        output = result.get("stdout", "")
        generated_files = result.get("generated_files", [])
        
        interpretation = {
            "summary": "変数間の相関関係を分析しました。",
            "findings": [],
            "strong_correlations": [],
            "weak_correlations": []
        }
        
        # 生成されたファイルから相関係数を読み取り
        correlation_data = self._read_correlation_data(generated_files)
        
        if correlation_data:
            # 強い相関を特定
            for pair, corr_value in correlation_data.items():
                if abs(corr_value) >= 0.7:
                    direction = "正の" if corr_value > 0 else "負の"
                    strength = self._get_correlation_strength(abs(corr_value))
                    finding = f"{pair}間には{strength}{direction}相関（{corr_value:.3f}）が見られます。"
                    interpretation["strong_correlations"].append(finding)
                elif abs(corr_value) <= 0.3:
                    interpretation["weak_correlations"].append(f"{pair}間の相関は弱い（{corr_value:.3f}）です。")
        
        # 解釈ガイドラインを適用
        correlation_guideline = self._find_guideline(knowledge, "correlation_interpret")
        if correlation_guideline:
            interpretation["guidance"] = correlation_guideline.get("caution", "")
        
        return interpretation
    
    def _interpret_t_test(self, result: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """t検定の解釈"""
        output = result.get("stdout", "")
        generated_files = result.get("generated_files", [])
        
        interpretation = {
            "summary": "2つのグループ間の平均値の差を統計的に検定しました。",
            "statistical_result": "",
            "practical_significance": "",
            "conclusion": ""
        }
        
        # t検定結果を読み取り
        t_test_data = self._read_t_test_data(generated_files, output)
        
        if t_test_data:
            p_value = t_test_data.get("p_value")
            if p_value is not None:
                # P値の解釈
                p_value_guideline = self._find_guideline(knowledge, "p_value_interpret")
                if p_value < 0.05:
                    interpretation["statistical_result"] = f"P値（{p_value:.4f}）は0.05より小さく、統計的に有意な差が認められます。"
                    if p_value_guideline:
                        interpretation["conclusion"] = p_value_guideline.get("template_significant", "").format(p_value=p_value)
                else:
                    interpretation["statistical_result"] = f"P値（{p_value:.4f}）は0.05以上で、統計的に有意な差は認められません。"
                    if p_value_guideline:
                        interpretation["conclusion"] = p_value_guideline.get("template_not_significant", "").format(p_value=p_value)
                
                # 実用的重要性の評価
                group1_mean = t_test_data.get("group1_mean")
                group2_mean = t_test_data.get("group2_mean")
                if group1_mean and group2_mean:
                    difference = abs(group1_mean - group2_mean)
                    interpretation["practical_significance"] = f"グループ間の平均値の差は{difference:.2f}です。"
        
        return interpretation
    
    def _interpret_regression(self, result: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """回帰分析の解釈"""
        output = result.get("stdout", "")
        generated_files = result.get("generated_files", [])
        
        interpretation = {
            "summary": "線形回帰分析を実行しました。",
            "model_performance": "",
            "feature_importance": [],
            "reliability": ""
        }
        
        # 回帰結果を読み取り
        regression_data = self._read_regression_data(generated_files, output)
        
        if regression_data:
            r2_score = regression_data.get("r2_score")
            if r2_score is not None:
                # R²スコアの解釈
                r2_interpretation = self._interpret_r2_score(r2_score)
                interpretation["model_performance"] = f"決定係数（R²）は{r2_score:.3f}で、{r2_interpretation}を示しています。"
                interpretation["reliability"] = f"モデルは目的変数の分散の{r2_score*100:.1f}%を説明しています。"
            
            # 回帰係数の解釈
            coefficients = regression_data.get("coefficients", [])
            feature_names = regression_data.get("feature_names", [])
            if coefficients and feature_names:
                for name, coef in zip(feature_names, coefficients):
                    direction = "正の" if coef > 0 else "負の"
                    magnitude = "強い" if abs(coef) > 1 else "弱い"
                    interpretation["feature_importance"].append(
                        f"{name}は目的変数に対して{magnitude}{direction}影響（係数: {coef:.3f}）を与えています。"
                    )
        
        return interpretation
    
    def _interpret_clustering(self, result: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """クラスタリングの解釈"""
        output = result.get("stdout", "")
        generated_files = result.get("generated_files", [])
        
        interpretation = {
            "summary": "K-meansクラスタリングを実行しました。",
            "cluster_quality": "",
            "cluster_characteristics": [],
            "business_insights": []
        }
        
        # クラスタリング結果を読み取り
        clustering_data = self._read_clustering_data(generated_files, output)
        
        if clustering_data:
            silhouette_score = clustering_data.get("silhouette_score")
            if silhouette_score is not None:
                # シルエット係数の解釈
                quality_assessment = self._interpret_silhouette_score(silhouette_score)
                interpretation["cluster_quality"] = f"シルエット係数は{silhouette_score:.3f}で、{quality_assessment}を示しています。"
            
            # クラスター数と分布
            cluster_counts = clustering_data.get("cluster_counts", [])
            if cluster_counts:
                total_samples = sum(cluster_counts)
                for i, count in enumerate(cluster_counts):
                    percentage = (count / total_samples) * 100
                    interpretation["cluster_characteristics"].append(
                        f"クラスター{i}: {count}件（{percentage:.1f}%）"
                    )
                
                # ビジネス的な洞察
                interpretation["business_insights"].append("各クラスターの特徴を詳しく分析し、ターゲットセグメントとして活用することを推奨します。")
        
        return interpretation
    
    def _interpret_general(self, result: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """一般的な結果の解釈"""
        return {
            "summary": f"{result.get('method_name', '分析')}が完了しました。",
            "execution_status": "成功" if result["success"] else "失敗",
            "execution_time": f"実行時間: {result.get('execution_time', 0):.2f}秒",
            "output_files": len(result.get("generated_files", []))
        }
    
    def _interpret_error(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """エラーの解釈"""
        error_info = result.get("error_info", {})
        
        interpretation = {
            "summary": f"{result.get('method_name', '分析')}でエラーが発生しました。",
            "error_type": error_info.get("type", "unknown"),
            "error_message": error_info.get("message", ""),
            "suggestions": error_info.get("suggestions", []),
            "next_steps": ["データを確認して再実行してください。"]
        }
        
        return interpretation
    
    def _extract_statistics_from_output(self, output: str) -> Dict[str, Dict[str, str]]:
        """出力から統計値を抽出"""
        stats_values = {}
        
        # 記述統計量のテーブルを解析
        lines = output.split('\n')
        current_variable = None
        
        for line in lines:
            line = line.strip()
            if 'count' in line and 'mean' in line:  # ヘッダー行
                continue
            elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s+\d+', line):  # 変数行
                parts = line.split()
                if len(parts) >= 8:
                    var_name = parts[0]
                    stats_values[var_name] = {
                        'count': parts[1],
                        'mean': parts[2],
                        'std': parts[3],
                        'min': parts[4],
                        '25%': parts[5],
                        '50%': parts[6],
                        '75%': parts[7],
                        'max': parts[8]
                    }
        
        return stats_values
    
    def _read_correlation_data(self, generated_files: List[Dict[str, Any]]) -> Dict[str, float]:
        """相関データを読み取り"""
        correlation_data = {}
        
        for file_info in generated_files:
            if file_info["name"] == "correlation_matrix.csv":
                try:
                    import pandas as pd
                    df = pd.read_csv(file_info["path"], index_col=0)
                    
                    # 上三角行列から相関係数を抽出
                    for i in range(len(df.columns)):
                        for j in range(i+1, len(df.columns)):
                            var1 = df.columns[i]
                            var2 = df.columns[j]
                            corr_value = df.iloc[i, j]
                            correlation_data[f"{var1}-{var2}"] = corr_value
                
                except Exception as e:
                    self.logger.warning(f"相関データの読み取りエラー: {e}")
        
        return correlation_data
    
    def _read_t_test_data(self, generated_files: List[Dict[str, Any]], output: str) -> Dict[str, Any]:
        """t検定データを読み取り"""
        t_test_data = {}
        
        # JSONファイルから読み取り
        for file_info in generated_files:
            if file_info["name"] == "t_test_result.json":
                try:
                    with open(file_info["path"], 'r', encoding='utf-8') as f:
                        t_test_data = json.load(f)
                except Exception as e:
                    self.logger.warning(f"t検定データの読み取りエラー: {e}")
        
        # 出力からも抽出を試行
        if not t_test_data:
            p_value_match = re.search(r'P値:\s*([\d\.]+)', output)
            if p_value_match:
                t_test_data["p_value"] = float(p_value_match.group(1))
        
        return t_test_data
    
    def _read_regression_data(self, generated_files: List[Dict[str, Any]], output: str) -> Dict[str, Any]:
        """回帰分析データを読み取り"""
        regression_data = {}
        
        for file_info in generated_files:
            if file_info["name"] == "regression_result.json":
                try:
                    with open(file_info["path"], 'r', encoding='utf-8') as f:
                        regression_data = json.load(f)
                except Exception as e:
                    self.logger.warning(f"回帰データの読み取りエラー: {e}")
        
        return regression_data
    
    def _read_clustering_data(self, generated_files: List[Dict[str, Any]], output: str) -> Dict[str, Any]:
        """クラスタリングデータを読み取り"""
        clustering_data = {}
        
        for file_info in generated_files:
            if file_info["name"] == "clustering_result.json":
                try:
                    with open(file_info["path"], 'r', encoding='utf-8') as f:
                        clustering_data = json.load(f)
                except Exception as e:
                    self.logger.warning(f"クラスタリングデータの読み取りエラー: {e}")
        
        return clustering_data
    
    def _find_guideline(self, knowledge: Dict[str, Any], guideline_id: str) -> Optional[Dict[str, Any]]:
        """特定のガイドラインを検索"""
        guidelines = knowledge.get("interpretation_guidelines", [])
        for guideline in guidelines:
            if guideline.get("id") == guideline_id:
                return guideline
        return None
    
    def _get_correlation_strength(self, abs_corr: float) -> str:
        """相関の強さを判定"""
        if abs_corr >= 0.8:
            return "非常に強い"
        elif abs_corr >= 0.6:
            return "強い"
        elif abs_corr >= 0.4:
            return "中程度の"
        elif abs_corr >= 0.2:
            return "弱い"
        else:
            return "非常に弱い"
    
    def _interpret_r2_score(self, r2: float) -> str:
        """R²スコアを解釈"""
        if r2 >= 0.9:
            return "非常に良い適合度"
        elif r2 >= 0.7:
            return "良い適合度"
        elif r2 >= 0.5:
            return "中程度の適合度"
        elif r2 >= 0.3:
            return "低い適合度"
        else:
            return "非常に低い適合度"
    
    def _interpret_silhouette_score(self, score: float) -> str:
        """シルエット係数を解釈"""
        if score >= 0.7:
            return "非常に良いクラスタリング"
        elif score >= 0.5:
            return "良いクラスタリング"
        elif score >= 0.3:
            return "中程度のクラスタリング"
        else:
            return "クラスタリング品質が低い"
    
    def _assess_interpretation_confidence(self, result: Dict[str, Any], interpretation: Dict[str, Any]) -> str:
        """解釈の信頼度を評価"""
        if not result["success"]:
            return "低"
        
        # 生成されたファイル数で判定
        file_count = len(result.get("generated_files", []))
        if file_count >= 2:
            return "高"
        elif file_count == 1:
            return "中"
        else:
            return "低"
    
    def _create_overall_interpretation(self, interpretations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """全体的な解釈を作成"""
        successful_interpretations = [i for i in interpretations if i.get("interpretation", {}).get("summary")]
        
        overall = {
            "summary": f"{len(successful_interpretations)}つの分析ステップが正常に完了しました。",
            "main_findings": [],
            "data_insights": [],
            "limitations": []
        }
        
        # 主要な発見を統合
        for interp in successful_interpretations:
            interpretation_data = interp.get("interpretation", {})
            
            # 要約を追加
            if "findings" in interpretation_data:
                overall["main_findings"].extend(interpretation_data["findings"])
            
            # データの洞察を追加
            if "data_characteristics" in interpretation_data:
                overall["data_insights"].extend(interpretation_data["data_characteristics"])
        
        return overall
    
    def _extract_key_insights(self, interpretations: List[Dict[str, Any]]) -> List[str]:
        """重要な洞察を抽出"""
        insights = []
        
        for interp in interpretations:
            interpretation_data = interp.get("interpretation", {})
            method_id = interp.get("method_id")
            
            # 手法別に重要な洞察を抽出
            if method_id == "correlation_analysis" and "strong_correlations" in interpretation_data:
                insights.extend(interpretation_data["strong_correlations"])
            elif method_id == "t_test_independent" and "conclusion" in interpretation_data:
                insights.append(interpretation_data["conclusion"])
            elif method_id == "linear_regression" and "model_performance" in interpretation_data:
                insights.append(interpretation_data["model_performance"])
        
        return insights[:5]  # 上位5つまで
    
    def _generate_recommendations(self, interpretations: List[Dict[str, Any]]) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        # 分析結果に基づく一般的な推奨事項
        successful_count = sum(1 for i in interpretations if i.get("interpretation", {}).get("summary"))
        
        if successful_count > 0:
            recommendations.append("分析結果を基に、ビジネス戦略やオペレーションの改善点を検討してください。")
            recommendations.append("さらに詳細な分析や追加データの収集を検討してください。")
        
        # エラーがある場合の推奨事項
        error_count = len(interpretations) - successful_count
        if error_count > 0:
            recommendations.append("エラーが発生したステップについて、データ品質やパラメータ設定を見直してください。")
        
        return recommendations
    
    def _assess_data_quality(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """データ品質を評価"""
        quality_assessment = {
            "overall_quality": "良好",
            "issues": [],
            "suggestions": []
        }
        
        # エラー率を計算
        total_steps = len(execution_results)
        error_steps = sum(1 for r in execution_results if not r["success"])
        error_rate = error_steps / total_steps if total_steps > 0 else 0
        
        if error_rate > 0.5:
            quality_assessment["overall_quality"] = "要改善"
            quality_assessment["issues"].append("多くのステップでエラーが発生しています")
            quality_assessment["suggestions"].append("データの前処理やクリーニングを実施してください")
        elif error_rate > 0.2:
            quality_assessment["overall_quality"] = "注意"
            quality_assessment["issues"].append("一部のステップでエラーが発生しています")
        
        return quality_assessment
