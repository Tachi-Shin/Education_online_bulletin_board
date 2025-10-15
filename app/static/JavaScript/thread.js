// static/JavaScript/thread.js

(() => {
  const THREAD_ID = window.THREAD_ID;
  const IS_LOGGED_IN = window.IS_LOGGED_IN;

  const postList = document.getElementById('postList');
  const olderBtn  = document.getElementById('olderBtn');
  const form      = document.getElementById('composerForm');
  const sendBtn   = document.getElementById('sendBtn');

  // クライアント側ページング
  const PAGE_SIZE = 20;
  let allPosts = [];     // サーバから取得した全件
  let shown = 0;         // 画面に出している件数

  // ---- 取得＆描画 ----
  async function fetchAllPosts() {
    const res = await fetch(`/api/thread/${THREAD_ID}/posts`);
    if (!res.ok) throw new Error('Failed to fetch posts');
    const data = await res.json();
    // created_at昇順が返る想定。念のためcreated_at→post_idで安定ソート
    allPosts = [...data].sort((a, b) => {
      if (a.created_at < b.created_at) return -1;
      if (a.created_at > b.created_at) return 1;
      return (a.post_id || 0) - (b.post_id || 0);
    });
  }

  function renderNextChunk() {
    const next = allPosts.slice(shown, shown + PAGE_SIZE);
    next.forEach(p => postList.appendChild(renderPost(p)));
    shown += next.length;
    toggleOlderBtn();
  }

  function toggleOlderBtn() {
    if (shown >= allPosts.length) {
      olderBtn.style.display = 'none';
    } else {
      olderBtn.style.display = '';
    }
  }

  function renderPost(post) {
    // ご指定レイアウト
    // <article class="post">
    //   <div class="post-header">
    //     <span class="post-user">@{{ post.user_id }}</span>
    //     <span class="post-timestamp">{{ post.created_at }}</span>
    //   </div>
    //   <div class="post-content">
    //     <p>{{ post.content }}</p>
    //     {% if post.file %}<img src="{{ post.file }}" alt="Attached image">{% endif %}
    //   </div>
    // </article>

    // サーバ側db.pyのall_posts_page()は:
    // - post.user_id = sender_id
    // - 画像なら post.file にURL
    // - それ以外は post.media_type / post.content_media で判定可能
    const article = document.createElement('article');
    article.className = 'post';

    const header = document.createElement('div');
    header.className = 'post-header';

    const user = document.createElement('span');
    user.className = 'post-user';
    user.textContent = `@${post.user_id ?? post.sender_id ?? 'unknown'}`;

    const ts = document.createElement('span');
    ts.className = 'post-timestamp';
    ts.textContent = post.created_at ?? '';

    header.appendChild(user);
    header.appendChild(ts);

    const body = document.createElement('div');
    body.className = 'post-content';

    if (post.content) {
      const p = document.createElement('p');
      p.textContent = post.content;
      body.appendChild(p);
    }

    // 互換: 画像は post.file に入っている
    if (post.file) {
      const img = document.createElement('img');
      img.src = post.file;
      img.alt = 'Attached image';
      img.loading = 'lazy';
      body.appendChild(img);
    } else if (post.content_media) {
      const mt = (post.media_type || '').toLowerCase();

      if (mt.startsWith('image')) {
        const img = document.createElement('img');
        img.src = post.content_media;
        img.alt = 'Attached image';
        img.loading = 'lazy';
        body.appendChild(img);
      } else if (mt.startsWith('video')) {
        const v = document.createElement('video');
        v.controls = true;
        v.src = post.content_media;

        v.controlsList = 'nodownload';
        v.disablePictureInPicture = true;
        v.addEventListener('contextmenu', e => e.preventDefault());

        body.appendChild(v);
      } else if (mt.startsWith('audio')) {
        const a = document.createElement('audio');
        a.controls = true;
        a.src = post.content_media;
        a.controlsList = 'nodownload';
        body.appendChild(a);
      } else if (mt) {
        const a = document.createElement('a');
        a.href = post.content_media;
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = `📎 ${post.original_name || 'ファイルを開く'}`;
        body.appendChild(a);
      }
    }

    article.appendChild(header);
    article.appendChild(body);
    return article;
  }

  // ---- 送信 ----
  async function handleSubmit(e) {
    e.preventDefault();
    if (!IS_LOGGED_IN) return;

    sendBtn.disabled = true;

    try {
      const fd = new FormData(form);
      // name属性は content / file / media_url になっている前提
      // 必須チェック：テキストもファイルもURLも無い場合は弾く（サーバ側も弾く実装）
      const hasContent = (fd.get('content') || '').trim().length > 0;
      const hasFile = fd.get('file') && fd.get('file').name;
      const hasUrl = (fd.get('media_url') || '').trim().length > 0;

      if (!hasContent && !hasFile && !hasUrl) {
        alert('内容が空です。テキスト、ファイル、またはURLのいずれかを入力してください。');
        return;
      }

      const res = await fetch(`/api/thread/${THREAD_ID}/post`, {
        method: 'POST',
        body: fd,
      });

      if (!res.ok) {
        const err = await safeJson(res);
        throw new Error(err?.error || '投稿に失敗しました');
      }

      // 成功したら一覧を再取得して末尾に差分描画でもいいが、
      // シンプルに全件再取得→再描画（小規模用途なら十分）
      await fetchAllPosts();
      postList.innerHTML = '';
      shown = 0;
      renderNextChunk();

      // フォームリセット
      form.reset();
    } catch (err) {
      console.error(err);
      alert(err.message || '投稿に失敗しました');
    } finally {
      sendBtn.disabled = false;
    }
  }

  async function safeJson(res) {
    try { return await res.json(); } catch { return null; }
  }

  // ---- 初期化 ----
  async function init() {
    try {
      await fetchAllPosts();
      renderNextChunk();
    } catch (e) {
      console.error(e);
      postList.innerHTML = '<p class="muted">投稿の取得に失敗しました。</p>';
      olderBtn.style.display = 'none';
    }
  }

  // イベント
  if (olderBtn) {
    olderBtn.addEventListener('click', () => {
      renderNextChunk();
    });
  }
  if (form) {
    form.addEventListener('submit', handleSubmit);
  }

  // go
  init();
})();
