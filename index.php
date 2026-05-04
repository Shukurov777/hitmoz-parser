<?php
// === НАСТРОЙКИ ===
$repo_name = 'hitmoz-parser';   // ← поменяй на имя своего репозитория
$github    = "https://github.com/Shukurov777/$repo_name";

// === API ===
if (isset($_GET['top-today'])) {
    header('Content-Type: application/json; charset=utf-8');
    echo shell_exec('python3 ' . escapeshellarg(__DIR__ . '/parser.py') . ' 2>&1');
    exit;
}

if (isset($_GET['search'])) {
    header('Content-Type: application/json; charset=utf-8');
    $query = trim($_GET['search']);
    if ($query === '') {
        echo json_encode(['success' => false, 'error' => 'Пустой запрос'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $cmd = 'python3 ' . escapeshellarg(__DIR__ . '/parser.py') . ' search ' . escapeshellarg($query);
    echo shell_exec($cmd . ' 2>&1');
    exit;
}
?>
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HitMoz Parser — Open Source API</title>
<style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{
        font-family:-apple-system,'Segoe UI',Roboto,sans-serif;
        background:#0a0a14;
        color:#e4e4e7;
        min-height:100vh;
        line-height:1.6;
    }
    .wrapper{max-width:860px;margin:0 auto;padding:60px 24px}

    /* Шапка */
    .hero{text-align:center;margin-bottom:50px}
    .badge{
        display:inline-block;
        background:rgba(168,85,247,.12);
        border:1px solid rgba(168,85,247,.3);
        color:#c4b5fd;
        padding:6px 14px;
        border-radius:20px;
        font-size:12px;
        font-weight:600;
        letter-spacing:.5px;
        text-transform:uppercase;
        margin-bottom:20px;
    }
    .hero h1{
        font-size:42px;
        font-weight:800;
        background:linear-gradient(135deg,#a855f7 0%,#ec4899 100%);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin-bottom:12px;
        letter-spacing:-1px;
    }
    .hero p{color:#9ca3af;font-size:17px;max-width:520px;margin:0 auto}
    .hero a.source{
        color:#60a5fa;
        text-decoration:none;
        font-weight:600;
    }
    .hero a.source:hover{text-decoration:underline}

    /* GitHub кнопка */
    .gh-btn{
        display:inline-flex;
        align-items:center;
        gap:8px;
        margin-top:22px;
        padding:11px 22px;
        background:#1f2937;
        border:1px solid #374151;
        color:#fff;
        text-decoration:none;
        border-radius:10px;
        font-weight:600;
        font-size:14px;
        transition:all .15s;
    }
    .gh-btn:hover{background:#374151;border-color:#a855f7}

    /* Секции */
    section{margin-bottom:36px}
    h2{
        font-size:13px;
        text-transform:uppercase;
        letter-spacing:1.5px;
        color:#6b7280;
        margin-bottom:14px;
        font-weight:700;
    }

    /* Карточки эндпоинтов */
    .card{
        background:#13131f;
        border:1px solid #1f1f33;
        border-radius:14px;
        padding:24px;
        transition:border-color .2s;
    }
    .card:hover{border-color:#2a2a4a}
    .card .method{
        display:inline-block;
        background:#065f46;
        color:#6ee7b7;
        font-size:11px;
        font-weight:700;
        padding:3px 8px;
        border-radius:4px;
        margin-right:8px;
    }
    .card code{
        font-family:'SF Mono','Monaco',monospace;
        color:#fbbf24;
        font-size:15px;
    }
    .card .desc{
        color:#9ca3af;
        margin-top:10px;
        font-size:14px;
    }
    .card a.try{
        display:inline-block;
        margin-top:14px;
        color:#60a5fa;
        text-decoration:none;
        font-size:13px;
        font-weight:600;
    }
    .card a.try:hover{color:#a855f7}

    /* Форма поиска */
    .search-form{
        display:flex;
        gap:8px;
        margin-top:14px;
    }
    .search-form input{
        flex:1;
        background:#0a0a14;
        border:1px solid #2a2a4a;
        color:#fff;
        padding:11px 14px;
        border-radius:9px;
        font-size:14px;
        font-family:inherit;
        outline:none;
        transition:border-color .15s;
    }
    .search-form input:focus{border-color:#a855f7}
    .search-form button{
        background:linear-gradient(135deg,#a855f7,#ec4899);
        color:#fff;
        border:0;
        padding:0 22px;
        border-radius:9px;
        cursor:pointer;
        font-weight:600;
        font-size:14px;
        transition:opacity .15s;
    }
    .search-form button:hover{opacity:.85}

    .examples{
        margin-top:14px;
        font-size:13px;
        color:#6b7280;
    }
    .examples a{
        color:#a78bfa;
        text-decoration:none;
        margin-right:10px;
    }
    .examples a:hover{text-decoration:underline}

    /* JSON блок */
    pre{
        background:#0a0a14;
        border:1px solid #1f1f33;
        border-radius:10px;
        padding:18px;
        overflow-x:auto;
        font-family:'SF Mono','Monaco',monospace;
        font-size:13px;
        color:#d1d5db;
    }
    .json-key{color:#60a5fa}
    .json-str{color:#86efac}
    .json-num{color:#fbbf24}

    /* Футер */
    footer{
        text-align:center;
        margin-top:60px;
        padding-top:30px;
        border-top:1px solid #1f1f33;
        color:#4b5563;
        font-size:13px;
    }
    footer a{color:#a78bfa;text-decoration:none}
    footer a:hover{text-decoration:underline}

    @media(max-width:560px){
        .hero h1{font-size:32px}
        .wrapper{padding:40px 18px}
    }
</style>
</head>
<body>

<div class="wrapper">

    <div class="hero">
        <div class="badge">⚡ Open Source · Python + PHP</div>
        <h1>HitMoz Parser API</h1>
        <p>Парсер музыкального сайта <a class="source" href="https://eu.hitmoz.com" target="_blank">eu.hitmoz.com</a> — отдаёт треки в чистом JSON. Топ-чарт и поиск по запросу.</p>
        <a class="gh-btn" href="<?= htmlspecialchars($github) ?>" target="_blank">
            <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
            Исходники на GitHub
        </a>
    </div>

    <section>
        <h2>📊 Топ-чарт</h2>
        <div class="card">
            <span class="method">GET</span>
            <code>?top-today</code>
            <div class="desc">Возвращает ~192 трека из топа за сегодня (4 страницы по 48 треков)</div>
            <a class="try" href="?top-today" target="_blank">Попробовать →</a>
        </div>
    </section>

    <section>
        <h2>🔍 Поиск</h2>
        <div class="card">
            <span class="method">GET</span>
            <code>?search={запрос}</code>
            <div class="desc">Поиск треков по названию, артисту или ключевому слову</div>

            <form class="search-form" method="get">
                <input type="text" name="search" placeholder="Введите имя артиста или название..." required>
                <button type="submit">Искать</button>
            </form>

            <div class="examples">
                Примеры:
                <a href="?search=Jony">Jony</a>
                <a href="?search=ЕГОР КРИД">ЕГОР КРИД</a>
                <a href="?search=SAYAN">SAYAN</a>
                <a href="?search=INSTASAMKA">INSTASAMKA</a>
            </div>
        </div>
    </section>

    <section>
        <h2>📦 Формат ответа</h2>
<pre>{
  <span class="json-key">"success"</span>: <span class="json-num">true</span>,
  <span class="json-key">"count"</span>: <span class="json-num">192</span>,
  <span class="json-key">"songs"</span>: [
    {
      <span class="json-key">"rank"</span>: <span class="json-num">1</span>,
      <span class="json-key">"title"</span>: <span class="json-str">"Камин"</span>,
      <span class="json-key">"artist"</span>: <span class="json-str">"EMIN, JONY"</span>,
      <span class="json-key">"duration"</span>: <span class="json-str">"03:08"</span>,
      <span class="json-key">"cover"</span>: <span class="json-str">"https://eu.hitmoz.com/..."</span>,
      <span class="json-key">"download"</span>: <span class="json-str">"https://eu.hitmoz.com/get/music/....mp3"</span>,
      <span class="json-key">"link"</span>: <span class="json-str">"https://eu.hitmoz.com/song/..."</span>
    }
  ]
}</pre>
    </section>

    <footer>
        <p>Open Source проект · MIT License · <a href="<?= htmlspecialchars($github) ?>" target="_blank">github.com/Shukurov777/<?= htmlspecialchars($repo_name) ?></a></p>
        <p style="margin-top:8px">Построен на <code style="color:#fbbf24">Python</code> + <code style="color:#fbbf24">PHP</code></p>
    </footer>

</div>

</body>
</html>
