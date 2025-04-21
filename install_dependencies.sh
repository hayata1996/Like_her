#!/bin/bash
# Like_her プロジェクトの依存関係をインストールするスクリプト

echo "Like Her - 依存関係インストールスクリプト"
echo "========================================"

# プロジェクトのルートディレクトリを設定
PROJECT_ROOT="$(pwd)"

# frontendの依存関係をインストール
echo "🔄 フロントエンド依存関係をインストール中..."
cd "$PROJECT_ROOT/app/frontend"
# 仮想環境を作成して有効化
uv venv
# 仮想環境にパッケージをインストール
uv pip install -r requirements.txt

# Streamlit依存関係で問題があれば、簡易版をインストール
if [ $? -ne 0 ]; then
  echo "⚠️ 一部のフロントエンド依存関係をインストールできませんでした。簡易版の依存関係をインストールします..."
  uv pip install streamlit plotly pandas numpy requests python-dotenv
fi

# APIの依存関係をインストール
echo "🔄 バックエンドAPI依存関係をインストール中..."
cd "$PROJECT_ROOT/app/api"
# 仮想環境を作成して有効化
uv venv
# 仮想環境にパッケージをインストール
uv pip install -r requirements.txt

# スケジューラーの依存関係をインストール
echo "🔄 スケジューラー依存関係をインストール中..."
cd "$PROJECT_ROOT/app/scheduler"
# 仮想環境を作成して有効化
uv venv
# 仮想環境にパッケージをインストール
uv pip install -r requirements.txt

echo "✅ インストール完了！"
echo ""
echo "🚀 アプリケーション実行方法："
echo "   - フロントエンド: cd $PROJECT_ROOT/app/frontend && streamlit run app.py"
echo "   - API: cd $PROJECT_ROOT/app/api && python main.py"
echo "   - スケジューラー: cd $PROJECT_ROOT/app/scheduler && python scheduler.py"