# /run.py
# アプリケーションのインスタンス(バックエンド(__init__.py)のアプリケーションそのもの)をインポート
from app import app

# アプリケーションを起動
if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)