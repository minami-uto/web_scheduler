# Web Scheduler

講座の日程調整を運営・受講者の両者で効率的に行うためのWebアプリケーションです。

## 🚀 機能

### 運営側
- 候補週（日付範囲）の設定
- 曜日ごとの時間候補のテンプレート入力
- アクティブな日時の選択と保存

### 受講者側（予定）
- 運営が選択した候補日時の表示
- 希望日時の選択・送信（※今後実装）

## 🖥️ 使用技術
- Python 3.x
- Flask
- HTML / Jinja2
- JSONファイルによるデータ保存

## 動作環境
- Pyhton 3.12
- Flask 3.1.1

## 実行方法

```bash
# 仮想環境の有効化（必要に応じて）
source ~/miniconda3/bin/activate

# Flask アプリの起動
python app.py
```

## 🔧 セットアップ方法

```bash
git clone https://github.com/your-username/web_scheduler.git
cd web_scheduler
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windowsなら venv\Scripts\activate
pip install -r requirements.txt
python app.py
