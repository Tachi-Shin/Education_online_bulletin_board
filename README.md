# SecProFlask

FlaskベースのWebアプリケーションです。  
このプロジェクトは、学内専用SNS・掲示板システムのバックエンドおよびUIを提供します。

---

## 🔧 環境構築手順

### Windows

```
python -V
python -m venv SecProFlask
SecProFlask\Scripts\activate
pip install -r requirements.txt
```
### Linux / macOS
```
python3 -V
python3 -m venv SecProFlask
source SecProFlask/bin/activate
pip install -r requirements.txt
```

🚀 アプリの起動
```
python run.py
```
または（Flask CLIを使用する場合）:
```
flask run
```
📁 ディレクトリ構成例
```
SecProFlask/
├── app/
│   ├── __init__.py
│   ├── index.py
│   ├── thread.py
│   ├── db.py
│   ├── static/
│   │   ├── css/
│   │   ├── JavaScript/
│   │   └── images/
│   └── templates/
│       ├── index.html
│       ├── thread.html
│       └── login.html
├── requirements.txt
├── run.py
└── README.md
```

📦 主な依存パッケージ
```
Flask
Flask-Mail
Werkzeug
python-dotenv
Pillow
simplejson
```
（requirements.txt に記載されています）

🧩 開発メモ
仮想環境を有効化してから開発を行ってください。

app/static/ 以下にはCSS・JavaScript・画像などの静的ファイルを配置します。

app/templates/ 以下にはJinja2テンプレート（HTML）を配置します。

データベースは app/db.py 経由でSQLiteまたはMySQLを操作します。

📝 ライセンス
© 2025 セキプロ2023年度入学生部員. All rights reserved.

