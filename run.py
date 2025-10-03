# /run.py
from app import app  # アプリケーションのインスタンスをインポート

# アプリケーションを起動
if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)