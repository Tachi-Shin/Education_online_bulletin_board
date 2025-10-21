function toggleRadioGroup() {
    var actionSelector = document.getElementById("action_selecter").value;
    var actionContent = document.getElementById("action_content");

    if (actionSelector === "search") {
        actionContent.innerHTML = `
            <h3 class="text_content">スレッドの検索</h3>
            <br>
            <input type="text" id="search_input" placeholder="キーワードで検索" class="styled-input">
            <button class="search-button" onclick="searchThread()">検索</button>
        `;
    } else if (actionSelector === "create") {
        actionContent.innerHTML = `
            <h3 class="text_content">スレッドの作成</h3>
            <br>
            <input type="text" id="thread_title" placeholder="スレッドタイトル" class="styled-input">
            <br>
            <br>
            <textarea id="thread_description" placeholder="スレッドの説明" class="styled-input"></textarea>
            <button class="create-button" onclick="createThread()">作成</button>
        `;
    }
}

function createThread() {
    var title = document.getElementById("thread_title").value;
    var description = document.getElementById("thread_description").value;
    var data = {
        action: "create",  // フォーム送信の意図を明示
        title: title,
        description: description
    };
    fetch("/", {  // `/create_thread` ではなく `/` に送る
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("エラー: " + data.error);
        } else {
            alert("スレッドが作成されました!");
            window.location.reload();  // ページをリロード
        }
    })
    .catch(error => console.error("Error:", error));
    return false;
}

function searchThread() {
  const input_text = document.getElementById("search_input").value;
  const data = { action: "search", search_value: input_text };

  fetch("/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(response => response.text())  // ← HTMLで受ける
    .then(html => {
      document.open();
      document.write(html);
      document.close();
    })
    .catch(err => console.error("search error:", err));

  return false;
}