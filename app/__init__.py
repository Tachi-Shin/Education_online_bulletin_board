# /app/__init__.py
from flask import Flask

# Flaskアプリケーションのインスタンス(バックエンドのアプリケーションそのもの)の作成
app = Flask(__name__)

# セッション管理用の秘密鍵
app.secret_key = 'SecProWebLearn'
# ルーティングやビュー関数のインポート
# これで `app` インスタンスを利用してルート(index.pyなどのPythonプログラム)を登録できる
from app.index import *
from app.login import *
from app.logout import *
from app.signup import *
from app.db import *
from app.cookie import *
from app.thread import *