#!/usr/bin/env python3
"""
Co-Analyst AI プロトタイプ統合テスト
フロントエンドプロトタイプとバックエンドシステムの統合テスト用スクリプト
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# プロジェクトディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import CoAnalystOrchestrator

def create_test_data():
    """テスト用のサンプルデータを作成"""
    print("🔧 テスト用サンプルデータを作成中...")
    
    # ランダムシードを設定
    np.random.seed(42)
    
    # サンプルデータの生成
    n_samples = 100
    dates = pd.date_range('2024-01-01', periods=n_samples, freq='D')
    
    test_data = pd.DataFrame({
        '日付': dates,
        '売上': np.random.normal(100000, 20000, n_samples),
        '広告費': np.random.normal(10000, 3000, n_samples),
        '顧客数': np.random.poisson(500, n_samples),
        'グループ': np.random.choice(['A', 'B'], n_samples),
        '地域': np.random.choice(['東京', '大阪', '名古屋'], n_samples)
    })
    
    # データディレクトリの作成
    os.makedirs('data', exist_ok=True)
    
    # CSVファイルとして保存
    test_file_path = 'data/test_data.csv'
    test_data.to_csv(test_file_path, index=False)
    
    print(f"✅ テストデータを作成しました: {test_file_path}")
    print(f"   - データサイズ: {test_data.shape}")
    print(f"   - 列: {list(test_data.columns)}")
    
    return test_file_path

def test_orchestrator_basic_functionality():
    """オーケストレーターの基本機能をテスト"""
    print("\n🧪 Co-Analyst AI オーケストレーター基本機能テスト")
    
    try:
        # オーケストレーターの初期化
        orchestrator = CoAnalystOrchestrator()
        print("✅ オーケストレーター初期化完了")
        
        # セッション開始
        session_id = orchestrator.start_session()
        print(f"✅ セッション開始: {session_id}")
        
        return orchestrator, session_id
        
    except Exception as e:
        print(f"❌ オーケストレーター初期化エラー: {e}")
        return None, None

def test_analysis_workflow(orchestrator, session_id):
    """分析ワークフローの統合テスト"""
    print("\n📊 分析ワークフロー統合テスト")
    
    test_queries = [
        "データの基本的な統計量を教えて",
        "売上と広告費の相関を分析して",
        "グループAとBの売上に差があるか検定して",
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 テスト {i}: '{query}'")
        
        try:
            # 分析実行
            result = orchestrator.process_user_input(query, session_id)
            
            if result["status"] == "success":
                print(f"✅ 分析成功")
                print(f"   - 実行ステップ数: {len(result['execution_results'])}")
                print(f"   - 応答生成: {'○' if result.get('response') else '×'}")
                
                # 成功したステップ数を確認
                successful_steps = sum(1 for r in result['execution_results'] if r.get('status') == 'completed')
                print(f"   - 成功ステップ: {successful_steps}/{len(result['execution_results'])}")
                
            else:
                print(f"❌ 分析失敗: {result.get('error', 'Unknown error')}")
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ 分析実行エラー: {e}")
            results.append({"status": "error", "error": str(e)})
    
    return results

def test_module_integration():
    """各モジュールの統合テスト"""
    print("\n🔧 モジュール統合テスト")
    
    try:
        # 意図解釈モジュールのテスト
        from modules.intent_parser import IntentParser
        intent_parser = IntentParser()
        
        test_input = "売上データの記述統計量を計算して"
        parsed_intent = intent_parser.parse(test_input)
        print(f"✅ 意図解釈モジュール: {parsed_intent['intent']['primary_intent']}")
        
        # RAG検索モジュールのテスト
        from modules.rag_searcher import RAGSearcher
        rag_searcher = RAGSearcher()
        
        relevant_knowledge = rag_searcher.search(parsed_intent)
        print(f"✅ RAG検索モジュール: {len(relevant_knowledge['analysis_methods'])}個の手法を発見")
        
        # タスクプランナーのテスト
        from modules.task_planner import TaskPlanner
        task_planner = TaskPlanner()
        
        analysis_plan = task_planner.create_plan(parsed_intent, relevant_knowledge)
        print(f"✅ タスクプランナー: {len(analysis_plan)}ステップの計画を作成")
        
        return True
        
    except Exception as e:
        print(f"❌ モジュール統合エラー: {e}")
        return False

def generate_test_report(results):
    """テスト結果レポートを生成"""
    print("\n📋 テスト結果レポート")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get("status") == "success")
    
    print(f"総テスト数: {total_tests}")
    print(f"成功テスト: {successful_tests}")
    print(f"成功率: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\n詳細結果:")
    for i, result in enumerate(results, 1):
        status = "✅ 成功" if result.get("status") == "success" else "❌ 失敗"
        print(f"  テスト {i}: {status}")
        
        if result.get("status") == "success":
            exec_results = result.get("execution_results", [])
            successful_steps = sum(1 for r in exec_results if r.get('status') == 'completed')
            print(f"    実行ステップ: {successful_steps}/{len(exec_results)}")
    
    print("\n" + "=" * 50)

def main():
    """メイン実行関数"""
    print("🚀 Co-Analyst AI プロトタイプ統合テスト開始")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. テストデータの作成
    test_data_path = create_test_data()
    
    # 2. オーケストレーターの基本機能テスト
    orchestrator, session_id = test_orchestrator_basic_functionality()
    
    if not orchestrator:
        print("❌ オーケストレーターの初期化に失敗しました。テストを中止します。")
        return
    
    # 3. モジュール統合テスト
    modules_ok = test_module_integration()
    
    if not modules_ok:
        print("⚠️ 一部モジュールで問題が発生しましたが、分析ワークフローテストを続行します。")
    
    # 4. 分析ワークフローテスト
    results = test_analysis_workflow(orchestrator, session_id)
    
    # 5. テスト結果レポート
    generate_test_report(results)
    
    print("\n🎉 Co-Analyst AI プロトタイプ統合テスト完了")

if __name__ == "__main__":
    main()
