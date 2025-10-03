(() => {
  const threadId = window.THREAD_ID;
  const isLoggedIn = !!window.IS_LOGGED_IN;
  const postList = document.getElementById('postList');
  const refreshBtn = document.getElementById('refreshBtn');
  const olderBtn = document.getElementById('olderBtn');

  let newestPostId = null;
  let oldestPostId = null;
  let loading = false;

  function postNode(p) {
    const el = document.createElement('article');
    el.className = 'post';
    el.dataset.postId = p.post_id;

    const meta = document.createElement('div');
    meta.className = 'post-meta';
    meta.textContent = `#${p.post_id}  ${p.sender} (id:${p.sender_id})  ${p.created_at}`;

    const body = document.createElement('div');
    body.className = 'post-content';
    body.innerText = p.content || '';

    el.appendChild(meta);
    el.appendChild(body);

    if (p.content_image) {
      const img = document.createElement('img');
      img.loading = 'lazy';
      img.alt = 'attached';
      img.src = p.content_image;
      el.appendChild(img);
    }
    return el;
  }

  async function fetchPosts({ newerThan=null, olderThan=null, limit=20 } = {}) {
    const qs = new URLSearchParams({ limit: String(limit) });
    if (newerThan) qs.set('newer_than', String(newerThan));
    if (olderThan) qs.set('older_than', String(olderThan));
    const res = await fetch(`/api/thread/${threadId}/posts?${qs}`, { credentials: 'same-origin' });
    if (!res.ok) throw new Error('fetch failed');
    const j = await res.json();
    return j.posts || [];
  }

  async function initialLoad() {
    if (loading) return;
    loading = true;
    try {
      const posts = await fetchPosts({ limit: 30 });
      postList.innerHTML = '';
      posts.forEach(p => postList.appendChild(postNode(p)));
      if (posts.length) {
        newestPostId = posts[0].post_id;
        oldestPostId = posts[posts.length - 1].post_id;
      }
    } finally { loading = false; }
  }

  async function refreshNew() {
    if (loading) return;
    loading = true;
    try {
      const posts = await fetchPosts({ newerThan: newestPostId, limit: 50 });
      for (let i = posts.length - 1; i >= 0; i--) {
        const p = posts[i];
        postList.prepend(postNode(p));
        if (!oldestPostId) oldestPostId = p.post_id;
      }
      if (posts.length) newestPostId = Math.max(newestPostId || 0, posts[0].post_id);
    } finally { loading = false; }
  }

  async function loadOlder() {
    if (loading) return;
    loading = true;
    try {
      const posts = await fetchPosts({ olderThan: oldestPostId, limit: 30 });
      posts.forEach(p => postList.appendChild(postNode(p)));
      if (posts.length) oldestPostId = posts[posts.length - 1].post_id;
    } finally { loading = false; }
  }

  // 投稿
  const form = document.getElementById('composerForm');
  if (form && isLoggedIn) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (loading) return;

      const content = document.getElementById('content').value.trim();
      const imageUrl = document.getElementById('imageUrl').value.trim();
      const file = document.getElementById('imageFile').files[0];

      if (!content && !imageUrl && !file) {
        alert('内容または画像を指定してください。');
        return;
      }

      const fd = new FormData();
      fd.append('content', content);
      if (imageUrl) fd.append('image_url', imageUrl);
      if (file) fd.append('image', file);

      loading = true;
      try {
        const res = await fetch(`/api/thread/${threadId}/post`, {
          method: 'POST',
          body: fd,
          credentials: 'same-origin',
        });
        if (!res.ok) throw new Error(await res.text());
        document.getElementById('content').value = '';
        document.getElementById('imageUrl').value = '';
        document.getElementById('imageFile').value = '';
        await refreshNew();
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      } catch (err) {
        alert('投稿に失敗しました: ' + err.message);
      } finally {
        loading = false;
      }
    });
  }

  // UIイベント
  if (refreshBtn) refreshBtn.addEventListener('click', refreshNew);
  if (olderBtn) olderBtn.addEventListener('click', loadOlder);

  // 初回・定期更新
  initialLoad();
  setInterval(() => { refreshNew().catch(()=>{}); }, 1000);
})();
