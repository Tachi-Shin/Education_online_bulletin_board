-- users テーブル
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) DEFAULT "風吹けば名無し",
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- threads テーブル
CREATE TABLE threads (
    thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 投稿（テキスト or メディア or 両方）
CREATE TABLE posts (
    post_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id      INTEGER NOT NULL,
    sender_id      INTEGER NOT NULL,
    content        TEXT,                   -- ← NOT NULL を外してメディアのみ投稿を許可
    content_media  TEXT,                   -- 保存URLまたはダウンロードエンドポイント
    media_type     TEXT,                   -- 'image' | 'video' | 'audio' | 'file'
    mime_type      TEXT,                   -- 例: 'image/png'
    original_name  TEXT,                   -- 元ファイル名（表示用）
    file_size      INTEGER,                -- バイト
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (thread_id) REFERENCES threads(thread_id) ON DELETE CASCADE
);