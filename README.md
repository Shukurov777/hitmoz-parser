<div align="center">

# 🎵 HitMoz Parser

**Парсер музыкального сайта [eu.hitmoz.com](https://eu.hitmoz.com) — отдаёт треки в формате JSON**

Получайте топ-чарты и результаты поиска через простой HTTP API на Python + PHP

[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PHP](https://img.shields.io/badge/PHP-7.4+-777BB4?style=flat-square&logo=php&logoColor=white)](https://www.php.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-❤️-ec4899?style=flat-square)](https://github.com/Shukurov777/hitmoz-parser)

[Возможности](#-возможности) ·
[Установка](#-установка) ·
[Использование](#-использование) ·
[API](#-api-endpoints) ·
[JSON](#-формат-ответа)

</div>

---

## 📖 О проекте

**HitMoz Parser** — это инструмент с открытым исходным кодом, который парсит музыкальный портал `eu.hitmoz.com` и отдаёт результаты в виде чистого JSON. Подходит для интеграции в свои приложения, ботов, мобильные клиенты или для аналитики.

Скрипт на **Python** делает основную работу (запрос → парсинг HTML → JSON), а лёгкий **PHP-скрипт** превращает его в HTTP-эндпоинт, который можно вызывать с любого устройства.

---

## ✨ Возможности

- 🔝 **Топ-чарт** — полный топ за сегодня (~192 трека, 4 страницы)
- 🔍 **Поиск** — по названию трека, имени артиста или ключевому слову
- 📦 **Чистый JSON** — никаких лишних обёрток, готовое API
- 🖼 **Полные данные** — название, артист, длительность, обложка, ссылка на скачивание `.mp3`
- 🌐 **Поддержка кириллицы** — корректные русские названия и имена
- ⚡ **Быстро** — без headless-браузеров, чистый `requests` + `BeautifulSoup`
- 🎨 **Стартовая страница** — красивый интерфейс с описанием API и формой поиска

---

## 🚀 Установка

### 1. Клонируем репозиторий

```bash
git clone https://github.com/Shukurov777/hitmoz-parser.git
cd hitmoz-parser
```

### 2. Устанавливаем зависимости Python

```bash
pip3 install -r requirements.txt
```

или вручную:

```bash
pip3 install requests beautifulsoup4
```

### 3. Готово!

Положи файлы на сервер с PHP и Python — всё.

---

## 🛠 Использование

### Через командную строку (терминал)

**Топ сегодня:**

```bash
python3 parser.py
```

**Поиск:**

```bash
python3 parser.py search "Jony"
python3 parser.py search "ЕГОР КРИД"
python3 parser.py search "Мальборо"
```

Скрипт выводит JSON в stdout — можно перенаправить в файл:

```bash
python3 parser.py > top.json
python3 parser.py search "Jony" > jony.json
```

### Через веб (HTTP API)

После того как закинул файлы на сервер с PHP, открывай в браузере:

| URL | Что делает |
|---|---|
| `index.php` | 🏠 Стартовая страница с описанием API |
| `index.php?top-today` | 📊 JSON с топ-чартом |
| `index.php?search=Jony` | 🔍 JSON с результатами поиска |

---

## 🔌 API Endpoints

### `GET /index.php?top-today`

Возвращает топ-чарт за сегодня — около 192 треков с 4 страниц сайта.

**Пример запроса:**

```bash
curl "https://your-domain.com/index.php?top-today"
```

---

### `GET /index.php?search={запрос}`

Поиск треков по любому слову.

**Параметры:**

| Параметр | Тип | Обязательный | Описание |
|---|---|---|---|
| `search` | string | ✅ | Имя артиста или название трека |

**Примеры запросов:**

```bash
# Поиск артиста на латинице
curl "https://your-domain.com/index.php?search=Jony"

# Поиск артиста на кириллице (URL-encoded)
curl "https://your-domain.com/index.php?search=%D0%95%D0%93%D0%9E%D0%A0%20%D0%9A%D0%A0%D0%98%D0%94"
```

В браузере просто напиши:

```
index.php?search=ЕГОР КРИД
```

---

## 📦 Формат ответа

### Успешный ответ

```json
{
  "success": true,
  "mode": "top-today",
  "source": "https://eu.hitmoz.com/songs/top-today",
  "count": 192,
  "songs": [
    {
      "rank": 1,
      "title": "Камин",
      "artist": "EMIN, JONY",
      "duration": "03:08",
      "cover": "https://eu.hitmoz.com/img/songs/81251971.jpg",
      "download": "https://eu.hitmoz.com/get/music/20260410/EMIN_JONY_-_Kamin_81251971.mp3",
      "link": "https://eu.hitmoz.com/song/81251971"
    },
    {
      "rank": 2,
      "title": "Дым",
      "artist": "ЕГОР КРИД, JONY",
      "duration": "02:53",
      "cover": "https://eu.hitmoz.com/img/songs/80591268.jpg",
      "download": "https://eu.hitmoz.com/get/music/20260103/EGOR_KRID_JONY_-_Dym_80591268.mp3",
      "link": "https://eu.hitmoz.com/song/80591268"
    }
  ]
}
```

### Описание полей

| Поле | Тип | Описание |
|---|---|---|
| `success` | bool | Успешен ли запрос |
| `mode` | string | Режим работы (`top-today` / `search`) |
| `query` | string | Поисковый запрос (только для `search`) |
| `source` | string | URL источника на сайте |
| `count` | int | Количество найденных треков |
| `songs[]` | array | Массив треков |

### Поля каждого трека

| Поле | Тип | Описание |
|---|---|---|
| `rank` | int | Позиция в списке (1, 2, 3...) |
| `title` | string | Название трека |
| `artist` | string | Имя артиста |
| `duration` | string | Длительность в формате `MM:SS` |
| `cover` | string | URL обложки (jpg/png) |
| `download` | string | Прямая ссылка на `.mp3` файл |
| `link` | string | Страница трека на сайте |

### Ошибка

```json
{
  "success": false,
  "error": "По запросу «xyz» ничего не найдено"
}
```

---

## 📁 Структура проекта

```
hitmoz-parser/
├── parser.py           # 🐍 Парсер на Python (вся логика)
├── index.php           # 🌐 PHP-обёртка + стартовая страница
├── requirements.txt    # 📦 Зависимости Python
├── README.md           # 📖 Этот файл
├── LICENSE             # ⚖️ Лицензия MIT
└── .gitignore          # 🚫 Исключения git
```

---

## 💡 Примеры использования

### Получить топ в JavaScript

```javascript
fetch('https://your-domain.com/index.php?top-today')
  .then(r => r.json())
  .then(data => {
    data.songs.forEach(song => {
      console.log(`${song.rank}. ${song.artist} — ${song.title}`);
    });
  });
```

### Поиск через Python

```python
import requests

r = requests.get('https://your-domain.com/index.php', params={'search': 'Jony'})
data = r.json()

for song in data['songs']:
    print(f"{song['artist']} — {song['title']} [{song['duration']}]")
    print(f"  ↓ {song['download']}")
```

### Скачать первый трек из топа

```bash
URL=$(curl -s "https://your-domain.com/index.php?top-today" | jq -r '.songs[0].download')
curl -O "$URL"
```

---

## ⚙️ Требования

- 🐍 **Python 3.7+**
- 🐘 **PHP 7.4+** (только если нужен HTTP API)
- 📦 **pip-пакеты:** `requests`, `beautifulsoup4`
- 🌐 На сервере должна быть включена функция `shell_exec()` в PHP

---

## ⚠️ Важно

> Этот проект создан **только в образовательных целях** для изучения техник веб-скрапинга и работы с HTML-парсерами. Все права на музыкальный контент принадлежат правообладателям и сайту `eu.hitmoz.com`. Используй ответственно и уважай terms of use исходного сайта.

---

## 🤝 Участие в проекте

Нашёл баг или хочешь предложить улучшение? Будем рады!

1. Сделай **Fork** репозитория
2. Создай свою ветку: `git checkout -b feature/awesome-feature`
3. Закоммить изменения: `git commit -m 'Add awesome feature'`
4. Запушь: `git push origin feature/awesome-feature`
5. Открой **Pull Request**

Также можешь:
- ⭐ Поставить звезду репозиторию
- 🐛 Создать [Issue](https://github.com/Shukurov777/hitmoz-parser/issues) с описанием бага
- 💡 Предложить новую фичу

---

## 📜 Лицензия

Проект распространяется под лицензией **MIT** — используй, изменяй, распространяй свободно. Подробности в файле [LICENSE](LICENSE).

---

## 👤 Автор

**Shukurov777**

- 💻 GitHub: [@Shukurov777](https://github.com/Shukurov777)

---

<div align="center">

**Если проект помог — поставь ⭐️ на GitHub!**

Сделано с 🖤 на Python + PHP

</div>
