# app/db.py
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import mimetypes
import time
import os

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}

# DB接続
def get_db_connection():
    db_name='app\KIT2ch.db'
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

# サインアップ
def signup_page_db(user_id, username, password_hash):
    conn = get_db_connection()
    cur = conn.cursor()
    try:        
        # 既存ユーザーチェック
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if cur.fetchone():
            return False, "この学籍番号は既に登録されています"

        # 新規ユーザー登録
        cur.execute("""
            INSERT INTO users 
            (user_id, username, password_hash, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, username, password_hash))

        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, f"データベースエラー: {str(e)}"
    except Exception as e:
        return False, f"予期せぬエラー: {str(e)}"
    finally:
        conn.close()

#ログイン
def login_page_db(user_id, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cur.fetchone()

        if not user:
            return False, None, "ユーザーが存在しません"

        stored_hash = user["password_hash"]
        if check_password_hash(stored_hash, password):
            return True, user["user_id"], user["username"]
        else:
            return False, None, "パスワードが正しくありません"

    except Exception as e:
        print("login_database エラー:", e)
        return False, None, "ログイン中にエラーが発生しました"

    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

#index.py
import logging

# スレッドの検索
def search_thread(search_value=None):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        if not search_value:  # Noneや空文字の場合は全件取得
            query = """
                SELECT t.thread_id, t.title, t.summary, t.created_at, t.view_count,
                       u.user_id AS creator_id, u.username AS creator
                FROM threads t
                JOIN users u ON t.creator_id = u.user_id
                ORDER BY t.created_at DESC
                LIMIT 100
            """
            cur.execute(query)
        else:
            query = """
                SELECT t.thread_id, t.title, t.summary, t.created_at, t.view_count,
                       u.user_id AS creator_id, u.username AS creator
                FROM threads t
                JOIN users u ON t.creator_id = u.user_id
                WHERE t.title LIKE ?
                   OR t.summary LIKE ?
                   OR u.username LIKE ?
                   OR u.user_id LIKE ?
                   OR t.thread_id LIKE ?
                ORDER BY t.created_at DESC
                LIMIT 100
            """
            search_pattern = f"%{search_value}%"
            cur.execute(query, (
                search_pattern,  # タイトル
                search_pattern,  # サマリー
                search_pattern,  # ユーザー名
                search_pattern,  # ユーザーID
                search_pattern   # スレッドID
            ))

        threads = cur.fetchall()
        return threads
    except Exception as e:
        logging.error(f"エラー: {e}")
        return []
    finally:
        conn.close()


#スレッドの作成検索
def create_thread(user_id, title, summary):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 新規スレッド登録
        cur.execute("""
            INSERT INTO threads 
            (creator_id,title, summary, created_at, view_count)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 0)
        """, (user_id, title, summary))
        conn.commit()
        print("スレッド作成済み")
    except Exception as e:
        print(f"エラー: {e}")
        return False
    finally:
        conn.close()

def thread_exists(thread_id: int) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM threads WHERE thread_id = ?", (thread_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

# ======投稿保存パス=====
def make_files_dir(thread_id: int) -> Path:
    upload_dir = Path(f"app/static/files/{thread_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

# ======投稿 追加（テキストのみ）=====
def not_file_insert_post_db(thread_id: int, sender_id: int, content: str) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO posts (
                thread_id, sender_id, content, content_media, media_type,
                mime_type, original_name, file_size, created_at
            )
            VALUES (?, ?, ?, NULL, NULL, NULL, NULL, NULL, CURRENT_TIMESTAMP)
        """, (thread_id, sender_id, content))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

# ======投稿 追加（ファイル or 外部URL）=====
def file_insert_post_db(thread_id, sender_id, content, file_storage, media_url) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        content_media = None
        media_type = None
        mime_type = None
        original_name = None
        file_size = None

        if file_storage and file_storage.filename:
            upload_dir = make_files_dir(thread_id)
            original_name = file_storage.filename

            # 1) まず保存名を作って保存
            ts = int(time.time())
            save_name = f"{ts}_{original_name}"
            save_path = upload_dir / save_name
            file_storage.save(save_path)

            file_size = save_path.stat().st_size

            # 2) MIME 推定（ブラウザ → ファイル名 → 保存名 の順）
            mime_type = (
                file_storage.mimetype
                or mimetypes.guess_type(original_name)[0]
                or mimetypes.guess_type(save_path.name)[0]
            )

            # 3) 画像判定の多段フォールバック
            ext = save_path.suffix.lower()
            is_image = False
            if mime_type and mime_type.startswith("image/"):
                is_image = True
            elif ext in IMAGE_EXTS:
                is_image = True
            else:
                # ヘッダの魔法数で最終確認（None 以外が返れば画像）
                try:
                    with Image.open(save_path) as img:
                        img.verify()  # 壊れた画像なら例外を出す
                    is_image = True
                    if not mime_type:
                        mime_type = f"image/{img.format.lower()}"
                except Exception:
                    pass

            if is_image:
                media_type = "image"
            elif mime_type and mime_type.startswith("video/"):
                media_type = "video"
            elif mime_type and mime_type.startswith("audio/"):
                media_type = "audio"
            else:
                media_type = "file"

            content_media = f"/static/files/{thread_id}/{save_name}"

        elif media_url:
            # 省略（既存でOK）：mime_type 推定 → media_type を image/video/audio/file のいずれかに
            # ※必要なら ext でも image 判定を足すと精度が上がります
            pass

        # --- DB 挿入（既存のまま） ---
        cur.execute("""
            INSERT INTO posts (
                thread_id, sender_id, content, content_media, media_type,
                mime_type, original_name, file_size, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            thread_id, sender_id, content if content else None,
            content_media, media_type, mime_type, original_name, file_size
        ))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

# ======投稿 取得（テンプレ用：画像パスを post['file'] に詰める）=====
def all_posts_page(thread_id: int) -> List[Dict]:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.post_id, p.thread_id, p.sender_id, p.content,
                   p.content_media, p.media_type, p.mime_type,
                   p.original_name, p.file_size, p.created_at,
                   u.username
            FROM posts p
            JOIN users u ON p.sender_id = u.user_id
            WHERE p.thread_id = ?
            ORDER BY p.created_at ASC, p.post_id ASC
        """, (thread_id,))
        rows = cur.fetchall()

        result = []
        for r in rows:
            d = dict(r)
            # テンプレ互換：画像なら file にパス/URLを入れる
            d["file"] = d["content_media"] if (d.get("media_type") == "image" and d.get("content_media")) else None
            # ご指定レイアウトに合わせて名前を合わせる（post.user_id）
            d["user_id"] = d["sender_id"]
            result.append(d)
        return result
    finally:
        conn.close()

# ======投稿 取得（API用：生データ）=====
def get_post_db(thread_id: int) -> List[Dict]:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.post_id, p.thread_id, p.sender_id, p.content,
                   p.content_media, p.media_type, p.mime_type,
                   p.original_name, p.file_size, p.created_at
            FROM posts p
            WHERE p.thread_id = ?
            ORDER BY p.created_at ASC, p.post_id ASC
        """, (thread_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()