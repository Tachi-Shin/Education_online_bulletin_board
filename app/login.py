# signup.py
from app import app
from flask import render_template, request, redirect, url_for, flash, session
from app.db import login_page_db
from app.cookie import create_login_cookie

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        success, user_id, username = login_page_db(user_id, password)
        if success:
            session['user_id'] = user_id
            flash(f"{username}さん、ようこそ！")

            response = redirect(url_for('index'))
            create_login_cookie(response, user_id, username)
            return response
        else:
            flash(username)  # エラーメッセージが2番目の値
            return render_template('login.html')

    return render_template('login.html')
