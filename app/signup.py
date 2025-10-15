# signup.py
from app import app
from flask import Flask, request, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash
from app.db import signup_page_db

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            user_id = int(request.form.get("user_id"))
            username = request.form.get("username")
            password = request.form.get("password")
            password_hash = generate_password_hash(password)

            # データベースに登録
            success, message = signup_page_db(user_id, username, password_hash)

            if success:
                flash("登録が完了しました。ログインしてください。", "success")
                return redirect(url_for("login"))
            else:
                flash(f"登録に失敗しました：{message}", "danger")
                return redirect(url_for("signup"))
        except ValueError:
            flash("学籍番号は数字で入力してください。", "danger")
            return redirect(url_for("signup"))
    return render_template('signup.html')

