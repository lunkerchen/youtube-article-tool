# YouTube 動画記事変換ツール 📺 ➡️ 📝

**yt-dlp** と **Google Gemini LLM** を活用し、YouTube動画を高精度で構造化された読みやすい記事に変換する高性能パイプラインです。

## 🌟 機能特性

- **多段階パイプライン**: `抽出 (Extraction)` -> `洗浄 (Cleaning)` -> `統合再構築 (Synthesis)`。
- **スマート字幕マッチング**: 優先順位リスト（繁体字中国語 -> 簡体字中国語 -> 英語 -> 日本語 -> 韓国語）に基づき、最適な字幕を自動選択します。
- **並列処理**: `asyncio` を使用し、複数のYouTubeリンクを同時に高速処理します。
- **構造化再構築**: Gemini 1.5 Flash を利用し、口語的な書き起こしを単純な要約ではなく「トピックブロック」形式の構造的な記事に再構成します。
- **柔軟な API キー管理**: 
    - Web UI での直接入力（ブラウザに一時保存され、再入力不要）。
    - 環境変数 `GEMINI_API_KEY` によるデフォルト設定。
- **堅牢なサムネイルシステム**: 最高解像度のサムネイルを自動マッチングし、フォールバックメカニズムにより常に表示を保証します。
- **変換履歴**: 変換した記事をローカルに保存し、後から簡単に参照可能です。

## 🛠️ 技術アーキテクチャ

1. **抽出 (Extraction)**: `yt-dlp` を使用してメタデータと `.vtt` 字幕ファイルを保存します。
2. **洗浄 (Cleaning)**: WEBVTT ヘッダー、タイムスタンプ、HTML タグを削除し、連続する重複行を排除します。
3. **統合再構築 (Synthesis)**: 専用プロンプトを用いて Gemini に以下の処理を指示します：
    - 内容を 3〜5 つのコアテーマに再構成。
    - 具体的な事例、データ、名言を保持。
    - 口語体をプロフェッショナルな書き言葉（中国語/日本語等）に変換。
    - 厳格な視覚的階層 (H1 -> H2 -> H3) を維持。

## 🚀 クイックスタート

### 🍎 macOS インストールガイド
**Homebrew** を使用するのが最速です：

1. **前提条件のインストール**
   ```bash
   brew install python yt-dlp
   ```
2. **プロジェクトのセットアップ**
   ```bash
   git clone https://github.com/lunkerchen/youtube-article-tool.git
   cd youtube-article-tool
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **起動**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   ブラウザで `http://localhost:8000` を開いてください。

### 🌐 一般的なインストール手順
1. リポジトリをクローンします。
2. 依存関係をインストール：`pip install -r requirements.txt`。
3. 起動：`./start.sh`。

## 📁 プロジェクト構造
- `main.py`: FastAPI バックエンドとコアロジック。
- `templates/index.html`: シングルページフロントエンド。
- `history.json`: 変換履歴のローカル保存ファイル。
- `start.sh`: クイックスタートスクリプト。

## 📝 ライセンス
MIT
