import os
from app import app
from datetime import datetime
from flask import request, jsonify, render_template
from werkzeug.utils import secure_filename

from app.db import fetch_thread_posts_page, insert_post_record, ensure_dirs
from app.cookie import has_login_cookie, get_user_id

ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}



@app.route("/thread/<int:thread_id>")
def thread(thread_id: int):
	is_logged_in = has_login_cookie()
	current_user_id = get_user_id() if is_logged_in else None
	return render_template(
		"thread.html",
		thread_id=thread_id,
		current_user_id=current_user_id,
		is_logged_in=is_logged_in,
	)

@app.post("/api/thread/<int:thread_id>/post")
def api_create_post(thread_id: int):
	if not has_login_cookie():
		return ("Unauthorized", 401)
	sender_id = get_user_id()
	if not sender_id:
		return ("Unauthorized", 401)

	content = (request.form.get("content") or "").strip()
	image_url = (request.form.get("image_url") or "").strip()
	content_image = None

	# URL指定
	if image_url:
		content_image = image_url

	# ファイルアップロード
	file = request.files.get("image")
	if file and file.filename:
		fname = secure_filename(file.filename)
		if not _allowed_image(fname):
			return ("Unsupported image format", 400)
		base, ext = os.path.splitext(fname)
		ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
		saved = f"{base}_{sender_id}_{ts}{ext}"
		save_dir = app.config["UPLOAD_FOLDER"]
		os.makedirs(save_dir, exist_ok=True)
		file.save(os.path.join(save_dir, saved))
		content_image = f"/static/uploads/{saved}"

	if not content and not content_image:
		return ("Empty content", 400)

	pid = insert_post_record(thread_id=thread_id, sender_id=sender_id, content=content, content_image=content_image)
	if not pid:
		return ("Insert failed", 500)
	return ("OK", 201)

def _allowed_image(name: str) -> bool:
    _, ext = os.path.splitext(name.lower())
    return ext in ALLOWED_IMAGE_EXT