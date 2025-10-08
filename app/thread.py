# app/thread.py
import os
from app import app
from flask import request, jsonify, render_template, redirect, url_for, abort
from app.db import (
    not_file_insert_post_db,
    file_insert_post_db,
    all_posts_page,
    get_post_db,
    thread_exists,
)
from app.cookie import has_login_cookie, get_user_id

# スレッドページ
@app.route("/thread/<int:thread_id>")
def thread(thread_id: int):
    is_logged_in = has_login_cookie()
    current_user_id = get_user_id() if is_logged_in else None

    if not is_logged_in:
        return redirect(url_for("signup"))

    if not thread_exists(thread_id):
        abort(404)

    contents = all_posts_page(thread_id)
    return render_template(
        "thread.html",
        thread_id=thread_id,
        contents=contents,
        is_logged_in=is_logged_in,
        current_user_id=current_user_id,
    )

# 投稿一覧API（JSON）
@app.get("/api/thread/<int:thread_id>/posts")
def api_get_posts(thread_id: int):
    if not thread_exists(thread_id):
        return jsonify({"error": "thread not found"}), 404
    posts = get_post_db(thread_id)
    return jsonify(posts), 200

# 投稿作成API
@app.post("/api/thread/<int:thread_id>/post")
def api_create_post(thread_id: int):
    if not has_login_cookie():
        return jsonify({"error": "unauthorized"}), 401

    if not thread_exists(thread_id):
        return jsonify({"error": "thread not found"}), 404

    sender_id = get_user_id()
    content = request.form.get("content", "").strip()
    file = request.files.get("file")
    media_url = request.form.get("media_url", "").strip()

    # どちらも無い場合はテキストのみ投稿（空文字OKにしない場合はチェックを）
    if not file and not media_url:
        if not content:
            return jsonify({"error": "content or file/media_url required"}), 400
        post_id = not_file_insert_post_db(thread_id, sender_id, content)
    else:
        post_id = file_insert_post_db(thread_id, sender_id, content, file, media_url)

    return jsonify({"ok": True, "post_id": post_id}), 201
