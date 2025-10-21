from app import app
from flask import render_template, request, redirect, url_for
from app.cookie import has_login_cookie, get_user_id
from app.db import search_thread, create_thread, view_thread

# --- GET: ページ表示 ---
@app.get('/')
def index():
    if not has_login_cookie():
        return redirect(url_for('signup'))

    user_id = get_user_id()
    main_threads = view_thread()
    return render_template('index.html', user_id=user_id, view="スレッド", threads=main_threads)


# --- POST: JSON アクション処理 ---
@app.post('/')
def index_post():
    if not has_login_cookie():
        return {"error": "未ログイン"}, 401

    user_id = get_user_id()
    data = request.get_json()
    action = data.get('action')

    if action == "create":
        title = data.get('title')
        summary = data.get('description')
        create_thread(user_id, title, summary)
        return {"message": "スレッド作成成功"}, 200

    if action == "search":
        search_value = data.get('search_value')
        search_threads = search_thread(search_value)
        return render_template('index.html', user_id=user_id, view="スレッドの検索結果", threads=search_threads)

    return {"error": "無効なアクション"}, 400
