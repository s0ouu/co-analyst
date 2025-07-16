// Main JavaScript for Co-Analyst AI Prototype
class CoAnalystApp {
    constructor() {
        this.currentData = null;
        this.currentChart = null;
        this.analysisInProgress = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showWelcomeState();
    }

    setupEventListeners() {
        // File upload
        const fileUploadArea = document.getElementById('fileUploadArea');
        const fileInput = document.getElementById('fileInput');
        const removeFileBtn = document.getElementById('removeFile');

        fileUploadArea.addEventListener('click', () => fileInput.click());
        fileUploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        fileUploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        fileUploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
        
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        removeFileBtn.addEventListener('click', this.removeFile.bind(this));

        // Quick analysis buttons
        const quickBtns = document.querySelectorAll('.quick-btn');
        quickBtns.forEach(btn => {
            btn.addEventListener('click', () => this.quickAnalysis(btn.dataset.analysis));
        });

        // Analysis method selection
        const analysisMethod = document.getElementById('analysisMethod');
        analysisMethod.addEventListener('change', this.handleMethodChange.bind(this));

        // Execute button
        const executeBtn = document.getElementById('executeBtn');
        executeBtn.addEventListener('click', this.executeAnalysis.bind(this));

        // Result actions
        const exportBtn = document.getElementById('exportBtn');
        const clearBtn = document.getElementById('clearBtn');
        
        exportBtn.addEventListener('click', this.exportResults.bind(this));
        clearBtn.addEventListener('click', this.clearResults.bind(this));

        // Analysis instructions
        const instructionsTextarea = document.getElementById('analysisInstructions');
        instructionsTextarea.addEventListener('input', this.validateInputs.bind(this));
    }

    // File handling
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.remove('dragover');
    }

    handleFileDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    async processFile(file) {
        if (!file.name.toLowerCase().endsWith('.csv')) {
            alert('CSVファイルのみサポートしています。');
            return;
        }

        try {
            // Show loading state
            this.showFileProcessing();
            
            // Process file using mock API
            this.currentData = await window.mockAPI.processFile(file);
            
            // Update UI
            this.showFileLoaded(file.name);
            this.validateInputs();
            
            console.log('Data loaded:', this.currentData);
        } catch (error) {
            console.error('File processing error:', error);
            alert('ファイルの処理中にエラーが発生しました。');
        }
    }

    showFileProcessing() {
        const fileUploadArea = document.getElementById('fileUploadArea');
        fileUploadArea.innerHTML = `
            <div class="spinner"></div>
            <p>ファイルを処理中...</p>
        `;
    }

    showFileLoaded(fileName) {
        const fileUploadArea = document.getElementById('fileUploadArea');
        const fileInfo = document.getElementById('fileInfo');
        const fileNameSpan = document.getElementById('fileName');
        
        fileUploadArea.style.display = 'none';
        fileInfo.style.display = 'flex';
        fileNameSpan.textContent = fileName;
    }

    removeFile() {
        const fileUploadArea = document.getElementById('fileUploadArea');
        const fileInfo = document.getElementById('fileInfo');
        const fileInput = document.getElementById('fileInput');
        
        this.currentData = null;
        fileInput.value = '';
        
        fileUploadArea.style.display = 'block';
        fileInfo.style.display = 'none';
        
        // Reset file upload area content
        fileUploadArea.innerHTML = `
            <i data-lucide="upload-cloud"></i>
            <p>CSVファイルをドラッグ&ドロップするか、クリックして選択</p>
        `;
        
        // Reinitialize icons
        lucide.createIcons();
        
        this.validateInputs();
        this.showWelcomeState();
    }

    // Analysis method handling
    handleMethodChange() {
        const method = document.getElementById('analysisMethod').value;
        this.showParameters(method);
        this.validateInputs();
    }

    showParameters(method) {
        const parametersSection = document.getElementById('parametersSection');
        const parametersContainer = document.getElementById('parametersContainer');
        
        if (!method || !this.currentData) {
            parametersSection.style.display = 'none';
            return;
        }

        const parameters = this.getMethodParameters(method);
        if (parameters.length === 0) {
            parametersSection.style.display = 'none';
            return;
        }

        parametersSection.style.display = 'block';
        parametersContainer.innerHTML = '';

        parameters.forEach(param => {
            const parameterDiv = document.createElement('div');
            parameterDiv.className = 'parameter-group';
            
            let input = '';
            if (param.type === 'list' && param.name === 'variables') {
                // Multiple select for variables
                const options = this.currentData.headers
                    .map(header => `<option value="${header}">${header}</option>`)
                    .join('');
                input = `<select multiple id="param_${param.name}" required="${param.required}">${options}</select>`;
            } else if (param.type === 'string' && param.name.includes('column')) {
                // Single select for column
                const options = this.currentData.headers
                    .map(header => `<option value="${header}">${header}</option>`)
                    .join('');
                input = `<select id="param_${param.name}" required="${param.required}"><option value="">選択してください</option>${options}</select>`;
            } else if (param.type === 'integer') {
                input = `<input type="number" id="param_${param.name}" min="1" required="${param.required}">`;
            } else {
                input = `<input type="text" id="param_${param.name}" required="${param.required}">`;
            }

            parameterDiv.innerHTML = `
                <label for="param_${param.name}">${param.name}</label>
                ${input}
                <div class="parameter-help">${param.description}</div>
            `;
            
            parametersContainer.appendChild(parameterDiv);
        });
    }

    getMethodParameters(method) {
        const parameterMap = {
            'desc_stats_summary': [
                { name: 'variables', type: 'list', description: '分析対象の変数を選択', required: true }
            ],
            't_test_independent': [
                { name: 'data_column', type: 'string', description: '数値データのある列', required: true },
                { name: 'group_column', type: 'string', description: 'グループを示すカテゴリカル列', required: true }
            ],
            'correlation_analysis': [
                { name: 'variables', type: 'list', description: '分析対象の変数を選択', required: true }
            ],
            'linear_regression': [
                { name: 'target_variable', type: 'string', description: '目的変数', required: true },
                { name: 'feature_variables', type: 'list', description: '説明変数のリスト', required: true }
            ],
            'kmeans_clustering': [
                { name: 'features', type: 'list', description: 'クラスタリングに使用する特徴量', required: true },
                { name: 'n_clusters', type: 'integer', description: 'クラスター数', required: true }
            ]
        };

        return parameterMap[method] || [];
    }

    // Quick analysis
    quickAnalysis(analysisType) {
        if (!this.currentData) {
            alert('先にデータファイルをアップロードしてください。');
            return;
        }

        const methodMap = {
            'desc_stats': 'desc_stats_summary',
            'correlation': 'correlation_analysis',
            'regression': 'linear_regression',
            'clustering': 'kmeans_clustering'
        };

        const method = methodMap[analysisType];
        document.getElementById('analysisMethod').value = method;
        this.handleMethodChange();
        
        // Auto-fill parameters with sensible defaults
        this.autoFillParameters(method);
    }

    autoFillParameters(method) {
        if (!this.currentData) return;

        const numericColumns = this.getNumericColumns();
        const allColumns = this.currentData.headers;

        switch (method) {
            case 'desc_stats_summary':
                this.setMultiSelectValues('param_variables', numericColumns.slice(0, 3));
                break;
            case 'correlation_analysis':
                this.setMultiSelectValues('param_variables', numericColumns.slice(0, 4));
                break;
            case 'linear_regression':
                if (numericColumns.length >= 2) {
                    this.setSelectValue('param_target_variable', numericColumns[0]);
                    this.setMultiSelectValues('param_feature_variables', numericColumns.slice(1, 3));
                }
                break;
            case 'kmeans_clustering':
                this.setMultiSelectValues('param_features', numericColumns.slice(0, 2));
                this.setInputValue('param_n_clusters', '3');
                break;
        }
    }

    getNumericColumns() {
        if (!this.currentData) return [];
        
        return this.currentData.headers.filter((header, index) => {
            const sample = this.currentData.rows.slice(0, 10).map(row => row[index]);
            return sample.every(val => !isNaN(parseFloat(val)) && isFinite(val));
        });
    }

    setSelectValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) element.value = value;
    }

    setMultiSelectValues(elementId, values) {
        const element = document.getElementById(elementId);
        if (element) {
            Array.from(element.options).forEach(option => {
                option.selected = values.includes(option.value);
            });
        }
    }

    setInputValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) element.value = value;
    }

    // Validation
    validateInputs() {
        const executeBtn = document.getElementById('executeBtn');
        const hasData = this.currentData !== null;
        const hasInstructions = document.getElementById('analysisInstructions').value.trim() !== '';
        const hasMethod = document.getElementById('analysisMethod').value !== '';
        
        const isValid = hasData && (hasInstructions || hasMethod) && !this.analysisInProgress;
        executeBtn.disabled = !isValid;
    }

    // Analysis execution
    async executeAnalysis() {
        if (this.analysisInProgress) return;

        try {
            this.analysisInProgress = true;
            this.validateInputs();
            
            const analysisConfig = this.buildAnalysisConfig();
            this.showProgressState();
            
            const result = await window.mockAPI.executeAnalysis(
                analysisConfig,
                this.updateProgress.bind(this)
            );
            
            this.showResults(result.result);
            
        } catch (error) {
            console.error('Analysis error:', error);
            alert('分析中にエラーが発生しました。');
            this.showWelcomeState();
        } finally {
            this.analysisInProgress = false;
            this.validateInputs();
        }
    }

    buildAnalysisConfig() {
        const method = document.getElementById('analysisMethod').value;
        const instructions = document.getElementById('analysisInstructions').value;
        
        const config = {
            method: method || 'generic_analysis',
            instructions: instructions,
            data: this.currentData,
            parameters: {}
        };

        // Collect parameters
        const parameterInputs = document.querySelectorAll('[id^="param_"]');
        parameterInputs.forEach(input => {
            const paramName = input.id.replace('param_', '');
            
            if (input.multiple) {
                config.parameters[paramName] = Array.from(input.selectedOptions).map(opt => opt.value);
            } else {
                config.parameters[paramName] = input.value;
            }
        });

        return config;
    }

    updateProgress(progressData) {
        const progressMessage = document.getElementById('progressMessage');
        const progressFill = document.getElementById('progressFill');
        const progressSteps = document.querySelectorAll('.step');

        if (progressMessage) {
            progressMessage.textContent = progressData.currentStepName;
        }

        if (progressFill) {
            progressFill.style.width = `${progressData.progress}%`;
        }

        // Update steps
        progressSteps.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            if (index < progressData.step - 1) {
                step.classList.add('completed');
            } else if (index === progressData.step - 1) {
                step.classList.add('active');
            }
        });
    }

    // State management
    showWelcomeState() {
        this.hideAllStates();
        document.getElementById('welcomeState').style.display = 'flex';
    }

    showProgressState() {
        this.hideAllStates();
        document.getElementById('progressState').style.display = 'flex';
        
        // Reset progress
        document.getElementById('progressFill').style.width = '0%';
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active', 'completed');
        });
    }

    showResults(result) {
        this.hideAllStates();
        document.getElementById('resultsState').style.display = 'block';
        
        this.renderResults(result);
        document.getElementById('exportBtn').disabled = false;
    }

    hideAllStates() {
        document.getElementById('welcomeState').style.display = 'none';
        document.getElementById('progressState').style.display = 'none';
        document.getElementById('resultsState').style.display = 'none';
    }

    // Results rendering
    renderResults(result) {
        this.renderSummary(result);
        this.renderChart(result);
        this.renderDetailedResults(result);
        this.renderInterpretation(result);
    }

    renderSummary(result) {
        const summaryCard = document.getElementById('summaryCard');
        const summary = result.summary;
        
        let summaryHTML = '<div class="summary-grid">';
        
        Object.entries(summary).forEach(([key, value]) => {
            const label = this.formatLabel(key);
            const formattedValue = this.formatValue(value);
            
            summaryHTML += `
                <div class="summary-item">
                    <div class="label">${label}</div>
                    <div class="value">${formattedValue}</div>
                </div>
            `;
        });
        
        summaryHTML += '</div>';
        summaryCard.innerHTML = summaryHTML;
    }

    renderChart(result) {
        const canvas = document.getElementById('analysisChart');
        const container = canvas.parentElement;
        
        // Destroy existing chart
        if (this.currentChart) {
            this.currentChart.destroy();
            this.currentChart = null;
        }

        if (!result.chartData) {
            container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">この分析タイプではグラフ表示はありません。</p>';
            return;
        }

        // Ensure canvas exists and is properly configured
        container.innerHTML = '<canvas id="analysisChart"></canvas>';
        const newCanvas = document.getElementById('analysisChart');
        const ctx = newCanvas.getContext('2d');
        
        // Create chart based on type
        try {
            const chartConfig = this.buildChartConfig(result.chartData);
            this.currentChart = new Chart(ctx, chartConfig);
            console.log('Chart created successfully:', this.currentChart);
        } catch (error) {
            console.error('Chart creation error:', error);
            container.innerHTML = '<p style="text-align: center; color: #ef4444; padding: 2rem;">グラフの表示でエラーが発生しました。</p>';
        }
    }

    buildChartConfig(chartData) {
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6
                }
            }
        };

        switch (chartData.type) {
            case 'histogram':
                return {
                    type: 'bar',
                    data: chartData,
                    options: {
                        ...commonOptions,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: '頻度'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: '値の範囲'
                                }
                            }
                        }
                    }
                };

            case 'scatter':
                return {
                    type: 'scatter',
                    data: chartData,
                    options: {
                        ...commonOptions,
                        scales: {
                            x: {
                                type: 'linear',
                                position: 'bottom'
                            },
                            y: {
                                type: 'linear'
                            }
                        }
                    }
                };

            case 'cluster_scatter':
                return {
                    type: 'scatter',
                    data: chartData,
                    options: {
                        ...commonOptions,
                        scales: {
                            x: {
                                type: 'linear',
                                position: 'bottom'
                            },
                            y: {
                                type: 'linear'
                            }
                        }
                    }
                };

            default:
                return {
                    type: 'bar',
                    data: chartData,
                    options: commonOptions
                };
        }
    }

    renderDetailedResults(result) {
        const detailedResults = document.getElementById('detailedResults');
        
        let html = '';
        
        if (result.statistics) {
            html += this.renderStatisticsTable(result.statistics);
        } else if (result.correlationMatrix) {
            html += this.renderCorrelationMatrix(result.correlationMatrix);
        } else if (result.model) {
            html += this.renderModelResults(result.model);
        } else if (result.clusters) {
            html += this.renderClusterResults(result.clusters);
        } else {
            html += '<p>詳細な結果データはありません。</p>';
        }
        
        detailedResults.innerHTML = html;
    }

    renderStatisticsTable(statistics) {
        let html = '<table class="results-table"><thead><tr>';
        html += '<th>変数</th><th>件数</th><th>平均</th><th>中央値</th><th>標準偏差</th><th>最小値</th><th>最大値</th>';
        html += '</tr></thead><tbody>';
        
        Object.entries(statistics).forEach(([variable, stats]) => {
            html += `<tr>
                <td>${variable}</td>
                <td>${stats.count}</td>
                <td>${stats.mean.toFixed(3)}</td>
                <td>${stats.median.toFixed(3)}</td>
                <td>${stats.std.toFixed(3)}</td>
                <td>${stats.min.toFixed(3)}</td>
                <td>${stats.max.toFixed(3)}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        return html;
    }

    renderCorrelationMatrix(matrix) {
        const variables = Object.keys(matrix);
        let html = '<table class="results-table"><thead><tr><th>変数</th>';
        
        variables.forEach(variable => {
            html += `<th>${variable}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        variables.forEach(variable1 => {
            html += `<tr><td><strong>${variable1}</strong></td>`;
            variables.forEach(variable2 => {
                const correlation = matrix[variable1][variable2];
                const cellClass = Math.abs(correlation) > 0.7 ? 'highlight' : '';
                html += `<td class="${cellClass}">${correlation.toFixed(3)}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        return html;
    }

    renderModelResults(model) {
        let html = '<div class="model-results">';
        html += '<h4>回帰係数</h4>';
        html += '<table class="results-table"><thead><tr><th>特徴量</th><th>係数</th></tr></thead><tbody>';
        
        model.features.forEach((feature, index) => {
            html += `<tr><td>${feature}</td><td>${model.coefficients[index].toFixed(4)}</td></tr>`;
        });
        
        html += `<tr><td><strong>切片</strong></td><td>${model.intercept.toFixed(4)}</td></tr>`;
        html += '</tbody></table></div>';
        
        return html;
    }

    renderClusterResults(clusters) {
        let html = '<div class="cluster-results">';
        html += '<h4>クラスター情報</h4>';
        html += `<p>総データ数: ${clusters.assignments.length}</p>`;
        
        const clusterCounts = {};
        clusters.assignments.forEach(cluster => {
            clusterCounts[cluster] = (clusterCounts[cluster] || 0) + 1;
        });
        
        html += '<table class="results-table"><thead><tr><th>クラスター</th><th>データ数</th><th>割合</th></tr></thead><tbody>';
        Object.entries(clusterCounts).forEach(([cluster, count]) => {
            const percentage = ((count / clusters.assignments.length) * 100).toFixed(1);
            html += `<tr><td>クラスター ${parseInt(cluster) + 1}</td><td>${count}</td><td>${percentage}%</td></tr>`;
        });
        html += '</tbody></table></div>';
        
        return html;
    }

    renderInterpretation(result) {
        const interpretationCard = document.getElementById('interpretationCard');
        const interpretation = result.interpretation;
        
        let html = '<div class="interpretation-content">';
        html += `<h4>${interpretation.summary}</h4>`;
        
        if (interpretation.details) {
            html += '<h5>詳細:</h5><ul>';
            interpretation.details.forEach(detail => {
                html += `<li>${detail}</li>`;
            });
            html += '</ul>';
        }
        
        if (interpretation.recommendations) {
            html += '<div class="advice"><h5>推奨事項:</h5><ul>';
            interpretation.recommendations.forEach(rec => {
                html += `<li>${rec}</li>`;
            });
            html += '</ul></div>';
        }
        
        html += '</div>';
        interpretationCard.innerHTML = html;
    }

    // Utility methods
    formatLabel(key) {
        const labelMap = {
            'totalRows': '総行数',
            'totalColumns': '総列数',
            'numericColumns': '数値列数',
            'analysisTime': '分析時刻',
            'variablesAnalyzed': '分析変数数',
            'strongCorrelations': '強相関ペア数',
            'targetVariable': '目的変数',
            'featureVariables': '説明変数',
            'r2Score': '決定係数',
            'rmse': 'RMSE',
            'numberOfClusters': 'クラスター数',
            'featuresUsed': '使用特徴量',
            'silhouetteScore': 'シルエット係数',
            'tStatistic': 't統計量',
            'pValue': 'P値',
            'group1Mean': 'グループ1平均',
            'group2Mean': 'グループ2平均',
            'isSignificant': '統計的有意性'
        };
        
        return labelMap[key] || key;
    }

    formatValue(value) {
        if (typeof value === 'number') {
            // Different formatting based on the size of the number
            if (value < 1 && value > -1) {
                return value.toFixed(4);
            } else if (value < 1000 && value > -1000) {
                return value.toFixed(2);
            } else {
                return value.toLocaleString('ja-JP');
            }
        } else if (typeof value === 'boolean') {
            return value ? 'はい' : 'いいえ';
        } else if (Array.isArray(value)) {
            return value.join(', ');
        } else {
            return value;
        }
    }

    // Export and clear
    exportResults() {
        // Simple export functionality
        const resultsData = {
            timestamp: new Date().toISOString(),
            analysis: this.buildAnalysisConfig(),
            // Add more export data as needed
        };
        
        const blob = new Blob([JSON.stringify(resultsData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `co_analyst_results_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    clearResults() {
        this.showWelcomeState();
        document.getElementById('exportBtn').disabled = true;
        
        if (this.currentChart) {
            this.currentChart.destroy();
            this.currentChart = null;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.coAnalystApp = new CoAnalystApp();
});
