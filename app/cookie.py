from flask import request
import itsdangerous

SECRET_KEY = 'your-secret-key'
serializer = itsdangerous.URLSafeTimedSerializer(SECRET_KEY)

# クッキーが存在するか確認
#index.py
def has_login_cookie():
    return 'login_token' in request.cookies

# クッキーを作成してレスポンスに付加
#login.py
def create_login_cookie(response, user_id, username):
    token = serializer.dumps(user_id)
    response.set_cookie('login_token', token, max_age=60*60*24*7)
    response.set_cookie('username', username, max_age=60*60*24*7)  # 表示用
    return response

# クッキーからuser_idを取得
def get_user_id():
    try:
        token = request.cookies.get('login_token')
        user_id = serializer.loads(token, max_age=3600*24*7)
        return user_id
    except Exception:
        return None

def logout_cookie(response):
    response.delete_cookie('login_token')
    response.delete_cookie('username')  # 表示用のクッキーも削除
    response.delete_cookie('session')
    return response