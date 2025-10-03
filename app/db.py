import sqlite3
from werkzeug.security import check_password_hash
from pathlib import Path
from typing import Optional

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


def ensure_dirs(app):
    # static/uploads を自動生成
    Path(app.static_folder, "uploads").mkdir(parents=True, exist_ok=True)

def fetch_thread_posts_page(thread_id: int, limit: int = 20, newer_than: Optional[int] = None, older_than: Optional[int] = None):
    params = [thread_id]
    where_extra = ""
    if newer_than is not None:
        where_extra = "AND p.post_id > ?"
        params.append(newer_than)
    elif older_than is not None:
        where_extra = "AND p.post_id < ?"
        params.append(older_than)

    sql = f"""
        SELECT p.post_id, p.thread_id, p.sender_id, u.username AS sender,
               p.content, p.content_image, p.created_at
        FROM posts p
        JOIN users u ON p.sender_id = u.user_id
        WHERE p.thread_id = ?
        {where_extra}
        ORDER BY p.post_id DESC
        LIMIT ?
    """
    params.append(limit)

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [
        {
            "post_id": r["post_id"],
            "thread_id": r["thread_id"],
            "sender_id": r["sender_id"],
            "sender": r["sender"],
            "content": r["content"] or "",
            "content_image": r["content_image"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]

def insert_post_record(thread_id: int, sender_id: int, content: str, content_image: Optional[str]):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO posts (thread_id, sender_id, content, content_image) VALUES (?, ?, ?, ?)",
            (thread_id, sender_id, content, content_image),
        )
        conn.commit()
        return cur.lastrowid