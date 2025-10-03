from app import app
from flask import render_template, request, redirect, url_for
from app.cookie import has_login_cookie, get_user_id
from app.db import create_thread, search_thread

@app.route('/', methods=['GET', 'POST'])
def index():
    if not has_login_cookie():
        return redirect(url_for('signup'))
    
    #Cookieからuser_id取得
    user_id = get_user_id()
    main_threads = search_thread()

    # 検索していないときはトレンドスレッドを表示
    if request.method == 'GET':
        return render_template('index.html', user_id=user_id, view="スレッド", threads=main_threads)
    
    
    if request.method == 'POST':
        data = request.get_json()
        print("受信データ:", data)  # 受信データを確認
        action = data.get('action')
        print(f"取得したアクション: {action}")  # action の値を確認

    if action == "create":
        title = data.get('title')
        summary = data.get('description')
        create_thread(user_id, title, summary)
        return {"message": "スレッド作成成功"}, 200

    if action == 'search':
        search_value = data.get('search_value')
        search_threads = search_thread(search_value)
        return render_template('index.html', user_id=user_id, view="スレッドの検索結果", threads=search_threads)
        
    return render_template('index.html')