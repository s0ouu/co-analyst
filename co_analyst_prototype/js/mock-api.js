// Mock API for Co-Analyst AI Prototype
class MockAPI {
    constructor() {
        this.analysisResults = new Map();
        this.progressCallbacks = new Map();
    }

    // Simulate file processing
    async processFile(file) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const text = e.target.result;
                    const lines = text.split('\n');
                    const headers = lines[0].split(',').map(h => h.trim());
                    const rows = lines.slice(1).filter(line => line.trim()).map(line => 
                        line.split(',').map(cell => cell.trim())
                    );
                    
                    resolve({
                        headers,
                        rows,
                        rowCount: rows.length,
                        columnCount: headers.length,
                        sample: rows.slice(0, 5)
                    });
                };
                reader.readAsText(file);
            }, 500);
        });
    }

    // Simulate analysis execution
    async executeAnalysis(analysisConfig, onProgress) {
        const analysisId = Date.now().toString();
        
        // Store progress callback
        if (onProgress) {
            this.progressCallbacks.set(analysisId, onProgress);
        }

        // Simulate analysis steps
        const steps = [
            { name: 'データ読み込み', duration: 1000 },
            { name: '前処理', duration: 1500 },
            { name: '分析実行', duration: 2000 },
            { name: '結果解釈', duration: 1000 },
            { name: 'レポート生成', duration: 500 }
        ];

        let totalProgress = 0;
        const progressIncrement = 100 / steps.length;

        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            if (onProgress) {
                onProgress({
                    step: i + 1,
                    totalSteps: steps.length,
                    currentStepName: step.name,
                    progress: totalProgress
                });
            }

            await this.delay(step.duration);
            totalProgress += progressIncrement;

            if (onProgress) {
                onProgress({
                    step: i + 1,
                    totalSteps: steps.length,
                    currentStepName: step.name,
                    progress: totalProgress,
                    completed: i === steps.length - 1
                });
            }
        }

        // Generate mock results based on analysis type
        const result = this.generateMockResult(analysisConfig);
        this.analysisResults.set(analysisId, result);

        return {
            analysisId,
            result
        };
    }

    // Generate mock analysis results
    generateMockResult(config) {
        const { method, parameters, data } = config;

        switch (method) {
            case 'desc_stats_summary':
                return this.generateDescriptiveStats(data);
            case 'correlation_analysis':
                return this.generateCorrelationAnalysis(data);
            case 'linear_regression':
                return this.generateRegressionAnalysis(data);
            case 'kmeans_clustering':
                return this.generateClusteringAnalysis(data);
            case 't_test_independent':
                return this.generateTTestAnalysis(data);
            default:
                return this.generateGenericAnalysis(data);
        }
    }

    generateDescriptiveStats(data) {
        const numericColumns = this.getNumericColumns(data);
        const stats = {};

        numericColumns.forEach(col => {
            const values = this.getColumnValues(data, col);
            stats[col] = {
                count: values.length,
                mean: this.calculateMean(values),
                median: this.calculateMedian(values),
                std: this.calculateStd(values),
                min: Math.min(...values),
                max: Math.max(...values),
                q25: this.calculatePercentile(values, 25),
                q75: this.calculatePercentile(values, 75)
            };
        });

        return {
            type: 'descriptive_stats',
            summary: {
                totalRows: data.rows.length,
                totalColumns: data.headers.length,
                numericColumns: numericColumns.length,
                analysisTime: new Date().toISOString()
            },
            statistics: stats,
            interpretation: this.generateStatsInterpretation(stats),
            chartData: this.generateHistogramData(data, numericColumns[0])
        };
    }

    generateCorrelationAnalysis(data) {
        const numericColumns = this.getNumericColumns(data);
        const correlationMatrix = {};

        numericColumns.forEach(col1 => {
            correlationMatrix[col1] = {};
            numericColumns.forEach(col2 => {
                if (col1 === col2) {
                    correlationMatrix[col1][col2] = 1.0;
                } else {
                    // Generate realistic correlation coefficient
                    correlationMatrix[col1][col2] = (Math.random() - 0.5) * 2 * 0.8;
                }
            });
        });

        return {
            type: 'correlation_analysis',
            summary: {
                variablesAnalyzed: numericColumns.length,
                strongCorrelations: this.countStrongCorrelations(correlationMatrix),
                analysisTime: new Date().toISOString()
            },
            correlationMatrix,
            interpretation: this.generateCorrelationInterpretation(correlationMatrix),
            chartData: this.generateCorrelationHeatmapData(correlationMatrix)
        };
    }

    generateRegressionAnalysis(data) {
        const numericColumns = this.getNumericColumns(data);
        const targetColumn = numericColumns[0];
        const features = numericColumns.slice(1, 3);

        const r2Score = 0.65 + Math.random() * 0.3; // 0.65-0.95
        const rmse = 10 + Math.random() * 20; // 10-30

        const coefficients = features.map(() => (Math.random() - 0.5) * 10);
        const intercept = Math.random() * 100;

        return {
            type: 'linear_regression',
            summary: {
                targetVariable: targetColumn,
                featureVariables: features,
                r2Score: r2Score,
                rmse: rmse,
                analysisTime: new Date().toISOString()
            },
            model: {
                coefficients: coefficients,
                intercept: intercept,
                features: features
            },
            interpretation: this.generateRegressionInterpretation(r2Score, rmse, coefficients, features),
            chartData: this.generateScatterPlotData(data, targetColumn, features[0])
        };
    }

    generateClusteringAnalysis(data) {
        const numericColumns = this.getNumericColumns(data);
        const nClusters = 3;
        const silhouetteScore = 0.3 + Math.random() * 0.4; // 0.3-0.7

        // Generate cluster assignments
        const clusterAssignments = data.rows.map(() => Math.floor(Math.random() * nClusters));
        
        return {
            type: 'kmeans_clustering',
            summary: {
                numberOfClusters: nClusters,
                featuresUsed: numericColumns.slice(0, 2),
                silhouetteScore: silhouetteScore,
                analysisTime: new Date().toISOString()
            },
            clusters: {
                assignments: clusterAssignments,
                centers: this.generateClusterCenters(nClusters, numericColumns.length)
            },
            interpretation: this.generateClusteringInterpretation(silhouetteScore, nClusters),
            chartData: this.generateClusterScatterData(data, numericColumns, clusterAssignments)
        };
    }

    generateTTestAnalysis(data) {
        const tStat = (Math.random() - 0.5) * 6; // -3 to 3
        const pValue = Math.random() * 0.1; // 0 to 0.1
        const group1Mean = 50 + Math.random() * 20;
        const group2Mean = group1Mean + (Math.random() - 0.5) * 15;

        return {
            type: 't_test_independent',
            summary: {
                tStatistic: tStat,
                pValue: pValue,
                group1Mean: group1Mean,
                group2Mean: group2Mean,
                isSignificant: pValue < 0.05,
                analysisTime: new Date().toISOString()
            },
            interpretation: this.generateTTestInterpretation(pValue, tStat, group1Mean, group2Mean),
            chartData: this.generateBoxPlotData(group1Mean, group2Mean)
        };
    }

    generateGenericAnalysis(data) {
        return {
            type: 'generic_analysis',
            summary: {
                dataShape: `${data.rows.length} rows × ${data.headers.length} columns`,
                analysisTime: new Date().toISOString(),
                status: 'completed'
            },
            interpretation: {
                summary: 'データの基本的な分析が完了しました。',
                details: [
                    `データセットには${data.rows.length}行、${data.headers.length}列が含まれています。`,
                    'より詳細な分析のために、特定の分析手法を選択してください。'
                ],
                recommendations: [
                    '記述統計量でデータの概要を把握する',
                    '相関分析で変数間の関係を調べる',
                    '回帰分析で予測モデルを構築する'
                ]
            },
            chartData: null
        };
    }

    // Helper methods
    getNumericColumns(data) {
        return data.headers.filter((header, index) => {
            const sample = data.rows.slice(0, 10).map(row => row[index]);
            return sample.every(val => !isNaN(parseFloat(val)) && isFinite(val));
        });
    }

    getColumnValues(data, columnName) {
        const columnIndex = data.headers.indexOf(columnName);
        return data.rows.map(row => parseFloat(row[columnIndex])).filter(val => !isNaN(val));
    }

    calculateMean(values) {
        return values.reduce((sum, val) => sum + val, 0) / values.length;
    }

    calculateMedian(values) {
        const sorted = [...values].sort((a, b) => a - b);
        const middle = Math.floor(sorted.length / 2);
        return sorted.length % 2 === 0 
            ? (sorted[middle - 1] + sorted[middle]) / 2 
            : sorted[middle];
    }

    calculateStd(values) {
        const mean = this.calculateMean(values);
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }

    calculatePercentile(values, percentile) {
        const sorted = [...values].sort((a, b) => a - b);
        const index = Math.floor((percentile / 100) * sorted.length);
        return sorted[index];
    }

    countStrongCorrelations(matrix) {
        let count = 0;
        const keys = Object.keys(matrix);
        for (let i = 0; i < keys.length; i++) {
            for (let j = i + 1; j < keys.length; j++) {
                if (Math.abs(matrix[keys[i]][keys[j]]) > 0.7) {
                    count++;
                }
            }
        }
        return count;
    }

    generateClusterCenters(nClusters, nFeatures) {
        const centers = [];
        for (let i = 0; i < nClusters; i++) {
            const center = [];
            for (let j = 0; j < nFeatures; j++) {
                center.push(Math.random() * 100);
            }
            centers.push(center);
        }
        return centers;
    }

    // Chart data generation methods
    generateHistogramData(data, columnName) {
        if (!columnName) return null;
        
        const values = this.getColumnValues(data, columnName);
        const bins = 10;
        const min = Math.min(...values);
        const max = Math.max(...values);
        const binWidth = (max - min) / bins;
        
        const histogram = new Array(bins).fill(0);
        const labels = [];
        
        values.forEach(val => {
            const binIndex = Math.min(Math.floor((val - min) / binWidth), bins - 1);
            histogram[binIndex]++;
        });
        
        for (let i = 0; i < bins; i++) {
            labels.push(`${(min + i * binWidth).toFixed(1)} - ${(min + (i + 1) * binWidth).toFixed(1)}`);
        }
        
        return {
            type: 'histogram',
            labels: labels,
            datasets: [{
                label: columnName,
                data: histogram,
                backgroundColor: 'rgba(102, 126, 234, 0.7)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1
            }]
        };
    }

    generateCorrelationHeatmapData(matrix) {
        const variables = Object.keys(matrix);
        
        // Create a simplified bar chart showing correlations for the first variable
        const firstVar = variables[0];
        const correlations = variables.slice(1).map(v => ({
            variable: v,
            correlation: matrix[firstVar][v]
        })).sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation));
        
        return {
            type: 'bar',
            labels: correlations.map(c => c.variable),
            datasets: [{
                label: `${firstVar}との相関`,
                data: correlations.map(c => c.correlation),
                backgroundColor: correlations.map(c => 
                    c.correlation > 0.5 ? '#10b981' : 
                    c.correlation < -0.5 ? '#ef4444' : '#6b7280'
                ),
                borderColor: correlations.map(c => 
                    c.correlation > 0.5 ? '#059669' : 
                    c.correlation < -0.5 ? '#dc2626' : '#4b5563'
                ),
                borderWidth: 1
            }]
        };
    }

    generateScatterPlotData(data, yColumn, xColumn) {
        if (!yColumn || !xColumn) return null;
        
        const xValues = this.getColumnValues(data, xColumn);
        const yValues = this.getColumnValues(data, yColumn);
        
        const plotData = xValues.map((x, i) => ({ x, y: yValues[i] })).filter(point => 
            !isNaN(point.x) && !isNaN(point.y)
        );
        
        return {
            type: 'scatter',
            datasets: [{
                label: `${yColumn} vs ${xColumn}`,
                data: plotData,
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: 'rgba(102, 126, 234, 1)'
            }]
        };
    }

    generateClusterScatterData(data, numericColumns, assignments) {
        if (numericColumns.length < 2) return null;
        
        const xColumn = numericColumns[0];
        const yColumn = numericColumns[1];
        const xValues = this.getColumnValues(data, xColumn);
        const yValues = this.getColumnValues(data, yColumn);
        
        const clusterColors = ['#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'];
        const datasets = {};
        
        assignments.forEach((cluster, i) => {
            if (!datasets[cluster]) {
                datasets[cluster] = {
                    label: `Cluster ${cluster + 1}`,
                    data: [],
                    backgroundColor: clusterColors[cluster % clusterColors.length]
                };
            }
            if (i < xValues.length && i < yValues.length) {
                datasets[cluster].data.push({ x: xValues[i], y: yValues[i] });
            }
        });
        
        return {
            type: 'cluster_scatter',
            datasets: Object.values(datasets)
        };
    }

    generateBoxPlotData(group1Mean, group2Mean) {
        return {
            type: 'boxplot',
            data: {
                group1: {
                    mean: group1Mean,
                    median: group1Mean + (Math.random() - 0.5) * 5,
                    q1: group1Mean - 10,
                    q3: group1Mean + 10,
                    min: group1Mean - 20,
                    max: group1Mean + 20
                },
                group2: {
                    mean: group2Mean,
                    median: group2Mean + (Math.random() - 0.5) * 5,
                    q1: group2Mean - 10,
                    q3: group2Mean + 10,
                    min: group2Mean - 20,
                    max: group2Mean + 20
                }
            }
        };
    }

    // Interpretation generation methods
    generateStatsInterpretation(stats) {
        const variables = Object.keys(stats);
        const firstVar = variables[0];
        const firstStats = stats[firstVar];
        
        return {
            summary: `${variables.length}個の数値変数について記述統計量を計算しました。`,
            details: [
                `${firstVar}の平均値は${firstStats.mean.toFixed(2)}、標準偏差は${firstStats.std.toFixed(2)}です。`,
                `データの範囲は${firstStats.min}から${firstStats.max}までです。`,
                `データの中央値は${firstStats.median.toFixed(2)}で、平均値との差は${Math.abs(firstStats.mean - firstStats.median).toFixed(2)}です。`
            ],
            recommendations: [
                '平均値と中央値の差が大きい場合、データが偏っている可能性があります',
                '標準偏差が大きい変数については、外れ値の確認を行ってください',
                '相関分析で変数間の関係を調べることをお勧めします'
            ]
        };
    }

    generateCorrelationInterpretation(matrix) {
        const strongCorrelations = this.countStrongCorrelations(matrix);
        const variables = Object.keys(matrix);
        
        return {
            summary: `${variables.length}個の変数間の相関分析を実行しました。`,
            details: [
                `${strongCorrelations}組の変数間で強い相関（|r| > 0.7）が見つかりました。`,
                '相関係数の範囲は-1から1で、0に近いほど相関が弱いことを示します。',
                '正の相関は一方が増えると他方も増える傾向を、負の相関は逆の傾向を示します。'
            ],
            recommendations: [
                '強い相関を示す変数ペアについて詳細な分析を行ってください',
                '相関関係は因果関係を意味しないことに注意してください',
                '多重共線性の問題を避けるため、回帰分析では高相関変数の組み合わせに注意してください'
            ]
        };
    }

    generateRegressionInterpretation(r2, rmse, coefficients, features) {
        let r2Quality = '低い';
        if (r2 > 0.7) r2Quality = '良い';
        else if (r2 > 0.5) r2Quality = '中程度の';
        
        return {
            summary: `線形回帰分析が完了しました。決定係数（R²）は${r2.toFixed(3)}です。`,
            details: [
                `モデルは目的変数の分散の${(r2 * 100).toFixed(1)}%を説明しています。`,
                `RMSE（平均平方二乗誤差の平方根）は${rmse.toFixed(2)}です。`,
                `${r2Quality}適合度のモデルが構築されました。`
            ],
            recommendations: [
                'R²が0.7以上の場合、良好なモデルと考えられます',
                'RMSEが小さいほど予測精度が高いことを示します',
                '残差の分析を行い、モデルの前提条件を確認してください'
            ]
        };
    }

    generateClusteringInterpretation(silhouetteScore, nClusters) {
        let quality = 'クラスタリング品質が低い';
        if (silhouetteScore > 0.5) quality = '良いクラスタリング';
        else if (silhouetteScore > 0.3) quality = '中程度のクラスタリング';
        
        return {
            summary: `K-meansクラスタリングにより${nClusters}個のクラスターに分割しました。`,
            details: [
                `シルエット係数は${silhouetteScore.toFixed(3)}で、これは${quality}を示しています。`,
                'シルエット係数は-1から1の値を取り、1に近いほど良いクラスタリングです。',
                '各クラスターの特徴を理解するために、クラスター別の統計量を確認してください。'
            ],
            recommendations: [
                'クラスター数を変更して最適な数を探索してください',
                '各クラスターの業務的な意味を解釈してください',
                '外れ値がクラスタリング結果に影響していないか確認してください'
            ]
        };
    }

    generateTTestInterpretation(pValue, tStat, group1Mean, group2Mean) {
        const isSignificant = pValue < 0.05;
        const meanDiff = Math.abs(group1Mean - group2Mean);
        
        return {
            summary: isSignificant 
                ? `統計的に有意な差が見つかりました（p = ${pValue.toFixed(4)} < 0.05）。`
                : `統計的に有意な差は見つかりませんでした（p = ${pValue.toFixed(4)} ≥ 0.05）。`,
            details: [
                `グループ1の平均: ${group1Mean.toFixed(2)}`,
                `グループ2の平均: ${group2Mean.toFixed(2)}`,
                `平均の差: ${meanDiff.toFixed(2)}`,
                `t統計量: ${tStat.toFixed(4)}`
            ],
            recommendations: isSignificant ? [
                '統計的有意性に加えて、実用的な重要性も検討してください',
                '効果サイズを計算して差の大きさを評価してください',
                'サンプルサイズが十分かどうか確認してください'
            ] : [
                'サンプルサイズが十分か確認してください',
                '他の統計的検定手法の適用を検討してください',
                '実際の差が小さい可能性があります'
            ]
        };
    }

    // Utility method for delay
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Create global instance
window.mockAPI = new MockAPI();
