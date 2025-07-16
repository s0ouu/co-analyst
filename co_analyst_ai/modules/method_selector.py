"""
手法・ツール選択モジュール
生成された分析ステップに対し、RAGで取得した知識から
具体的な分析手法や使用すべきライブラリ/関数、コードテンプレートなどを選択
"""
import logging
from typing import Dict, List, Any, Optional

class MethodSelector:
    """分析手法とツールを選択するクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def select(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析ステップに対して最適な手法を選択
        
        Args:
            step: 実行するステップの詳細
            
        Returns:
            選択された手法の詳細情報
        """
        method_id = step.get("method_id")
        self.logger.info(f"手法選択開始: {method_id}")
        
        # 基本的な手法マッピング
        method_mapping = self._get_method_mapping()
        
        if method_id in method_mapping:
            selected_method = method_mapping[method_id]
        else:
            # デフォルト手法
            selected_method = self._get_default_method(step)
        
        # パラメータの調整
        adjusted_method = self._adjust_parameters(selected_method, step)
        
        self.logger.info(f"手法選択完了: {adjusted_method['name']}")
        return adjusted_method
    
    def _get_method_mapping(self) -> Dict[str, Dict[str, Any]]:
        """手法IDと実装の対応を定義"""
        return {
            "data_load": {
                "id": "data_load",
                "name": "データロード",
                "library": "pandas",
                "function": "read_csv",
                "template_type": "data_io",
                "code_template": "import pandas as pd\ndf = pd.read_csv('{data_path}')\nprint(f'データサイズ: {df.shape}')\nprint(df.head())"
            },
            "data_load_info": {
                "id": "data_load_info", 
                "name": "データロードと情報確認",
                "library": "pandas",
                "function": "info",
                "template_type": "data_exploration",
                "code_template": "import pandas as pd\ndf = pd.read_csv('{data_path}')\nprint('=== データ基本情報 ===')\nprint(f'データサイズ: {df.shape}')\nprint('\\n=== データ型情報 ===')\nprint(df.dtypes)\nprint('\\n=== 最初の5行 ===')\nprint(df.head())\nprint('\\n=== 基本統計量 ===')\nprint(df.describe())"
            },
            "desc_stats_summary": {
                "id": "desc_stats_summary",
                "name": "記述統計量要約",
                "library": "pandas",
                "function": "describe",
                "template_type": "statistical_analysis",
                "code_template": "import pandas as pd\ndf = pd.read_csv('{data_path}')\n{variables_filter}result = df.describe()\nprint('=== 記述統計量 ===')\nprint(result)\nresult.to_csv('{output_path}/desc_stats.csv')"
            },
            "correlation_analysis": {
                "id": "correlation_analysis",
                "name": "相関分析",
                "library": "pandas, matplotlib, seaborn",
                "function": "corr",
                "template_type": "correlation",
                "code_template": "import pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport numpy as np\ndf = pd.read_csv('{data_path}')\n# 数値列のみ選択\nnumeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()\ncorr_matrix = df[numeric_cols].corr()\nprint('=== 相関行列 ===')\nprint(corr_matrix)\n# ヒートマップ作成\nplt.figure(figsize=(10, 8))\nsns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, square=True)\nplt.title('変数間相関ヒートマップ')\nplt.tight_layout()\nplt.savefig('{output_path}/correlation_heatmap.png', dpi=300, bbox_inches='tight')\nplt.close()\ncorr_matrix.to_csv('{output_path}/correlation_matrix.csv')"
            },
            "t_test_independent": {
                "id": "t_test_independent", 
                "name": "独立2標本t検定",
                "library": "scipy, pandas",
                "function": "ttest_ind",
                "template_type": "hypothesis_testing",
                "code_template": "from scipy import stats\nimport pandas as pd\nimport numpy as np\ndf = pd.read_csv('{data_path}')\n# グループの確認\ngroups = df['{group_column}'].unique()\nprint(f'グループ: {groups}')\nif len(groups) != 2:\n    print('警告: t検定には2つのグループが必要です')\n    exit()\ngroup1_data = df[df['{group_column}'] == groups[0]]['{data_column}'].dropna()\ngroup2_data = df[df['{group_column}'] == groups[1]]['{data_column}'].dropna()\nprint(f'グループ1 ({groups[0]}): 平均={group1_data.mean():.4f}, 標準偏差={group1_data.std():.4f}, サンプル数={len(group1_data)}')\nprint(f'グループ2 ({groups[1]}): 平均={group2_data.mean():.4f}, 標準偏差={group2_data.std():.4f}, サンプル数={len(group2_data)}')\nt_stat, p_value = stats.ttest_ind(group1_data, group2_data)\nprint(f'\\n=== t検定結果 ===')\nprint(f'T統計量: {t_stat:.4f}')\nprint(f'P値: {p_value:.4f}')\nif p_value < 0.05:\n    print('結論: 有意水準5%で統計的に有意な差があります')\nelse:\n    print('結論: 有意水準5%で統計的に有意な差は認められません')\nresult = {'t_statistic': t_stat, 'p_value': p_value, 'group1_mean': group1_data.mean(), 'group2_mean': group2_data.mean(), 'group1_std': group1_data.std(), 'group2_std': group2_data.std()}\nimport json\nwith open('{output_path}/t_test_result.json', 'w', encoding='utf-8') as f:\n    json.dump(result, f, ensure_ascii=False, indent=2)"
            },
            "linear_regression": {
                "id": "linear_regression",
                "name": "線形回帰分析", 
                "library": "scikit-learn, pandas, matplotlib",
                "function": "LinearRegression",
                "template_type": "machine_learning",
                "code_template": "import pandas as pd\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import r2_score, mean_squared_error\nimport matplotlib.pyplot as plt\nimport numpy as np\ndf = pd.read_csv('{data_path}')\n# 欠損値の除去\ndf_clean = df.dropna()\nX = df_clean[{feature_variables}]\ny = df_clean['{target_variable}']\nprint(f'使用データ数: {len(df_clean)}')\nprint(f'説明変数: {list(X.columns)}')\nprint(f'目的変数: {y.name}')\nmodel = LinearRegression()\nmodel.fit(X, y)\ny_pred = model.predict(X)\nr2 = r2_score(y, y_pred)\nrmse = np.sqrt(mean_squared_error(y, y_pred))\nprint(f'\\n=== 回帰分析結果 ===')\nprint(f'決定係数 (R²): {r2:.4f}')\nprint(f'RMSE: {rmse:.4f}')\nprint(f'切片: {model.intercept_:.4f}')\nfor i, coef in enumerate(model.coef_):\n    print(f'{X.columns[i]}の回帰係数: {coef:.4f}')\n# 散布図と回帰直線（単回帰の場合）\nif len(X.columns) == 1:\n    plt.figure(figsize=(10, 6))\n    plt.scatter(X.iloc[:, 0], y, alpha=0.6, label='実測値')\n    plt.plot(X.iloc[:, 0], y_pred, color='red', label='回帰直線')\n    plt.xlabel(X.columns[0])\n    plt.ylabel(y.name)\n    plt.title(f'回帰分析結果 (R² = {r2:.3f})')\n    plt.legend()\n    plt.savefig('{output_path}/regression_plot.png', dpi=300, bbox_inches='tight')\n    plt.close()\nresult = {'r2_score': r2, 'rmse': rmse, 'coefficients': model.coef_.tolist(), 'intercept': model.intercept_, 'feature_names': list(X.columns)}\nimport json\nwith open('{output_path}/regression_result.json', 'w', encoding='utf-8') as f:\n    json.dump(result, f, ensure_ascii=False, indent=2)"
            },
            "kmeans_clustering": {
                "id": "kmeans_clustering",
                "name": "K-meansクラスタリング",
                "library": "scikit-learn, pandas, matplotlib",
                "function": "KMeans",
                "template_type": "machine_learning",
                "code_template": "import pandas as pd\nfrom sklearn.cluster import KMeans\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.metrics import silhouette_score\nimport matplotlib.pyplot as plt\nimport numpy as np\ndf = pd.read_csv('{data_path}')\n# 欠損値の除去\ndf_clean = df.dropna()\nX = df_clean[{features}]\nprint(f'クラスタリング対象データ数: {len(df_clean)}')\nprint(f'使用特徴量: {list(X.columns)}')\n# 標準化\nscaler = StandardScaler()\nX_scaled = scaler.fit_transform(X)\n# K-meansクラスタリング\nkmeans = KMeans(n_clusters={n_clusters}, random_state=42, n_init=10)\ncluster_labels = kmeans.fit_predict(X_scaled)\n# シルエット係数の計算\nsilhouette_avg = silhouette_score(X_scaled, cluster_labels)\nprint(f'\\n=== クラスタリング結果 ===')\nprint(f'クラスター数: {kmeans.n_clusters}')\nprint(f'シルエット係数: {silhouette_avg:.4f}')\n# 各クラスターの統計情報\ndf_clean['cluster'] = cluster_labels\nfor cluster_id in range(kmeans.n_clusters):\n    cluster_data = df_clean[df_clean['cluster'] == cluster_id]\n    print(f'\\nクラスター {cluster_id}: {len(cluster_data)}件')\n    print(cluster_data[{features}].describe())\n# クラスタリング結果の保存\ndf_clean.to_csv('{output_path}/clustered_data.csv', index=False)\n# 2次元での可視化（最初の2つの特徴量）\nif len({features}) >= 2:\n    plt.figure(figsize=(10, 8))\n    scatter = plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=cluster_labels, cmap='viridis', alpha=0.7)\n    plt.colorbar(scatter)\n    plt.xlabel(f'{X.columns[0]} (標準化済み)')\n    plt.ylabel(f'{X.columns[1]} (標準化済み)')\n    plt.title(f'K-meansクラスタリング結果 (シルエット係数: {silhouette_avg:.3f})')\n    plt.savefig('{output_path}/clustering_plot.png', dpi=300, bbox_inches='tight')\n    plt.close()\nresult = {'silhouette_score': silhouette_avg, 'n_clusters': kmeans.n_clusters, 'cluster_centers': kmeans.cluster_centers_.tolist(), 'cluster_counts': [int(sum(cluster_labels == i)) for i in range(kmeans.n_clusters)]}\nimport json\nwith open('{output_path}/clustering_result.json', 'w', encoding='utf-8') as f:\n    json.dump(result, f, ensure_ascii=False, indent=2)"
            },
            "data_quality_check": {
                "id": "data_quality_check",
                "name": "データ品質確認",
                "library": "pandas",
                "function": "isnull",
                "template_type": "data_exploration", 
                "code_template": "import pandas as pd\nimport numpy as np\ndf = pd.read_csv('{data_path}')\nprint('=== データ品質レポート ===')\nprint(f'総行数: {len(df)}')\nprint(f'総列数: {len(df.columns)}')\nprint('\\n=== 欠損値情報 ===')\nmissing_info = df.isnull().sum()\nmissing_percent = (missing_info / len(df)) * 100\nmissing_df = pd.DataFrame({{\n    '欠損値数': missing_info,\n    '欠損率(%)': missing_percent\n}})\nprint(missing_df[missing_df['欠損値数'] > 0])\nprint('\\n=== データ型情報 ===')\nprint(df.dtypes.value_counts())\nprint('\\n=== 数値列の外れ値チェック ===')\nnumeric_cols = df.select_dtypes(include=[np.number]).columns\nfor col in numeric_cols:\n    Q1 = df[col].quantile(0.25)\n    Q3 = df[col].quantile(0.75)\n    IQR = Q3 - Q1\n    lower_bound = Q1 - 1.5 * IQR\n    upper_bound = Q3 + 1.5 * IQR\n    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]\n    print(f'{col}: 外れ値候補 {len(outliers)}件 ({len(outliers)/len(df)*100:.1f}%)')\nquality_report = {{\n    'total_rows': len(df),\n    'total_columns': len(df.columns),\n    'missing_values': missing_info.to_dict(),\n    'data_types': df.dtypes.astype(str).to_dict()\n}}\nimport json\nwith open('{output_path}/data_quality_report.json', 'w', encoding='utf-8') as f:\n    json.dump(quality_report, f, ensure_ascii=False, indent=2)"
            },
            "convert_to_datetime": {
                "id": "convert_to_datetime",
                "name": "日付型変換",
                "library": "pandas", 
                "function": "to_datetime",
                "template_type": "data_processing",
                "code_template": "import pandas as pd\ndf = pd.read_csv('{data_path}')\nprint(f'変換前の{column}のデータ型: {df[\\'{column}\\'].dtype}')\nprint(f'変換前のサンプル値:')\nprint(df['{column}'].head())\ntry:\n    df['{column}'] = pd.to_datetime(df['{column}'])\n    print(f'\\n変換後の{column}のデータ型: {df[\\'{column}\\'].dtype}')\n    print(f'日付範囲: {df[\\'{column}\\'].min()} から {df[\\'{column}\\'].max()}')\n    df.to_csv('{output_path}/datetime_converted.csv', index=False)\n    print(f'変換済みデータを保存しました: {output_path}/datetime_converted.csv')\nexcept Exception as e:\n    print(f'日付変換エラー: {e}')\n    print('日付フォーマットを確認してください')"
            },
            "aggregate_by_month": {
                "id": "aggregate_by_month",
                "name": "月別集計",
                "library": "pandas",
                "function": "groupby",
                "template_type": "data_processing",
                "code_template": "import pandas as pd\ndf = pd.read_csv('{data_path}')\ndf['{date_column}'] = pd.to_datetime(df['{date_column}'])\ndf['year_month'] = df['{date_column}'].dt.to_period('M')\nagg_method = '{aggregation}' if '{aggregation}' else 'sum'\nprint(f'集計方法: {agg_method}')\nprint(f'集計対象列: {value_column}')\nif agg_method == 'sum':\n    monthly_data = df.groupby('year_month')['{value_column}'].sum().reset_index()\nelif agg_method == 'mean':\n    monthly_data = df.groupby('year_month')['{value_column}'].mean().reset_index()\nelif agg_method == 'count':\n    monthly_data = df.groupby('year_month')['{value_column}'].count().reset_index()\nelse:\n    monthly_data = df.groupby('year_month')['{value_column}'].sum().reset_index()\nmonthly_data['year_month'] = monthly_data['year_month'].astype(str)\nprint('\\n=== 月別集計結果 ===')\nprint(monthly_data)\nmonthly_data.to_csv('{output_path}/monthly_aggregated.csv', index=False)\nprint(f'月別集計データを保存しました: {output_path}/monthly_aggregated.csv')"
            },
            "line_chart": {
                "id": "line_chart",
                "name": "折れ線グラフ作成",
                "library": "matplotlib, pandas",
                "function": "plot",
                "template_type": "visualization",
                "code_template": "import pandas as pd\nimport matplotlib.pyplot as plt\nimport matplotlib.dates as mdates\nfrom datetime import datetime\n# 日本語フォント設定\nplt.rcParams['font.family'] = 'DejaVu Sans'\n# データ読み込み\ndf = pd.read_csv('{data_path}')\nif 'year_month' in df.columns:\n    df['date'] = pd.to_datetime(df['year_month'])\nelse:\n    df['date'] = pd.to_datetime(df['{x_axis}'])\nplt.figure(figsize=(12, 6))\nplt.plot(df['date'], df['{y_axis}'], marker='o', linewidth=2, markersize=6)\nplt.title('{title}', fontsize=16, fontweight='bold')\nplt.xlabel('日付', fontsize=12)\nplt.ylabel('{y_axis}', fontsize=12)\nplt.grid(True, alpha=0.3)\nplt.xticks(rotation=45)\nplt.tight_layout()\nplt.savefig('{output_path}/line_chart.png', dpi=300, bbox_inches='tight')\nplt.close()\nprint(f'折れ線グラフを作成しました: {output_path}/line_chart.png')"
            }
        }
    
    def _get_default_method(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """デフォルト手法を返す"""
        return {
            "id": "default",
            "name": "デフォルト処理",
            "library": "pandas", 
            "function": "basic",
            "template_type": "general",
            "code_template": "import pandas as pd\n# デフォルト処理\nprint('処理を実行中...')"
        }
    
    def _adjust_parameters(self, method: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        """ステップのパラメータに基づいて手法を調整"""
        # ステップのパラメータを手法に統合
        if "parameters" in step:
            method["parameters"] = step["parameters"]
        
        # 特定の手法に対する調整
        method_id = method["id"]
        
        if method_id == "kmeans_clustering":
            # クラスター数のデフォルト設定
            if "parameters" not in method:
                method["parameters"] = {}
            if "n_clusters" not in method["parameters"]:
                method["parameters"]["n_clusters"] = 4
        
        elif method_id == "desc_stats_summary":
            # 変数フィルターの設定
            if "parameters" in method and "variables" in method["parameters"]:
                variables = method["parameters"]["variables"]
                if variables:
                    method["variables_filter"] = f"selected_vars = {variables}\ndf = df[selected_vars]\n"
                else:
                    method["variables_filter"] = "# 全ての数値変数を使用\n"
            else:
                method["variables_filter"] = "# 全ての数値変数を使用\n"
        
        return method
