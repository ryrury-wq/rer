from flask import render_template_string

# Главная страница
index_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Контроль сроков</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
            overflow-x: hidden;
        }
        .items-container {
            max-height: 65vh;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        .item { 
            padding: 10px; 
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .item-info { flex-grow: 1; }
        .move-btn {
            width: 24px;
            height: 24px;
            border: 1px solid #999;
            background: white;
            cursor: pointer;
            margin-left: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .expired { background-color: #ffdddd; }
        .warning { background-color: #ffcc99; }
        .soon { background-color: #ffffcc; }
        .normal { background-color: white; }
        .nav-links {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        .nav-links a {
            padding: 8px 12px;
            background: #f0f0f0;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
        }
        h1 {
            font-size: 1.5em;
            margin: 0 0 10px 0;
        }
    </style>
</head>
<body>
    <h1>Товары с истекающим сроком</h1>
    <div class="nav-links">
        <a href="/scan">Сканировать</a>
        <a href="/history">История</a>
    </div>
    <hr>
    <div class="items-container">
        {% for item in items %}
            <div class="item {{ item.status }}">
                <div class="item-info">
                    <strong>{{ item.name }}</strong> ({{ item.barcode }})<br>
                    Годен до: {{ item.expiration_date }}<br>
                    
                    {% if item.days_since_expiry > 0 %}
                        Просрочено на : {{ item.days_since_expiry }} дня(дней)
                        <br>Удаление через: {{ item.days_until_removal }} дней
                    {% else %}
                        До истечения: {{ item.days_until_expiry }} дней
                        <br>Удаление через: {{ item.days_until_removal }} дней ({{ item.removal_date }})
                    {% endif %}
                </div>
                <form action="/move_to_history" method="POST" style="display: inline;">
                    <input type="hidden" name="batch_id" value="{{ item.id }}">
                    <button type="submit" class="move-btn" title="Переместить в историю">→</button>
                </form>
            </div>
        {% else %}
            <p>Нет товаров с истекающим сроком</p>
        {% endfor %}
    </div>
</body>
</html>
'''

scan_html = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Сканирование</title>
    <style>
        body { 
            font-family: sans-serif; 
            padding: 10px; 
            margin: 0; 
            background: #f9f9f9; 
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
        }
        .scanner-container { 
            position: relative; 
            width: 90%; 
            max-width: 400px;
            height: 200px;
            margin: 0 auto 15px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        video { 
            width: 100%; 
            height: 100%; 
            object-fit: cover;
        }
        .overlay { 
            position: absolute; 
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%; 
            height: 40%; 
            border: 2px dashed red; 
            border-radius: 8px; 
            pointer-events: none; 
            box-sizing: border-box;
        }
        form { 
            width: 90%;
            max-width: 400px;
            margin-top: 10px; 
        }
        input[type="text"], input[type="date"], input[type="number"], select {
            width: 100%; 
            padding: 12px; 
            font-size: 1em; 
            border: 1px solid #ccc;
            border-radius: 4px; 
            margin-bottom: 10px; 
            background: #fff; 
            box-sizing: border-box;
        }
        button { 
            width: 100%; 
            padding: 12px; 
            background-color: #28a745; 
            color: white;
            font-size: 1.1em; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
            margin-top: 10px;
        }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        .scanner-instruction {
            text-align: center;
            margin: 10px 0 15px;
            font-size: 0.9em;
            color: #666;
        }
        h1 {
            font-size: 1.5em;
            margin: 5px 0 10px;
        }
    </style>
</head>
<body>
    <h1>Сканирование товара</h1>
    
    <div class="scanner-instruction">
        Поместите штрих-код в рамку
    </div>

    <div class="scanner-container">
        <video id="video" autoplay playsinline></video>
        <div class="overlay"></div>
    </div>

    <form method="POST">
        <!-- Форма без изменений -->
    </form>

    <script type="module">
        // Скрипт без изменений
    </script>
</body>
</html>
'''

# Обновим остальные шаблоны аналогично
new_product_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Новый товар</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
        }
        form {
            max-width: 400px;
            margin: 0 auto;
        }
        input, button { 
            width: 100%;
            box-sizing: border-box;
            padding: 12px; 
            margin: 5px 0; 
        }
        h1 {
            font-size: 1.5em;
        }
    </style>
</head>
<body>
    <h1>Добавление нового товара</h1>
    <form method="POST">
        <label>Штрих-код:</label>
        <input type="text" name="barcode" value="{{ barcode }}" readonly>
        <label>Название товара:</label>
        <input type="text" name="name" required>
        <button type="submit">Сохранить</button>
    </form>
</body>
</html>
'''

add_batch_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Добавить срок</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
        }
        form {
            max-width: 400px;
            margin: 0 auto;
        }
        input, button { 
            width: 100%;
            box-sizing: border-box;
            padding: 12px; 
            margin: 5px 0; 
        }
        h1 {
            font-size: 1.5em;
        }
    </style>
</head>
<body>
    <h1>Добавление срока годности для: {{ product_name }}</h1>
    <form method="POST">
        <label>Срок годности:</label>
        <input type="date" name="expiration_date" required>
        <button type="submit">Добавить</button>
    </form>
</body>
</html>
'''

history_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>История</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
        }
        .items-container {
            max-height: 70vh;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        li { 
            padding: 8px; 
            border-bottom: 1px solid #eee; 
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .item-info { flex-grow: 1; }
        .restore-btn {
            width: 24px;
            height: 24px;
            border: 1px solid #999;
            background: white;
            cursor: pointer;
            margin-left: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .nav-links {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        .nav-links a {
            padding: 8px 12px;
            background: #f0f0f0;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
        }
        h1 {
            font-size: 1.5em;
            margin: 0 0 10px 0;
        }
    </style>
</head>
<body>
    <h1>История списанных товаров</h1>
    <div class="nav-links">
        <a href="/">На главную</a>
    </div>
    <hr>
    <div class="items-container">
        <ul>
            {% for item in history_items %}
                <li>
                    <div class="item-info">
                        <strong>{{ item['product_name'] }}</strong> ({{ item['barcode'] }})<br>
                        Срок годности: {{ item['expiration_date'] }}<br>
                        Удален: {{ item['removed_date'] }}
                    </div>
                    <form action="/restore_from_history" method="POST" style="display: inline;">
                        <input type="hidden" name="history_id" value="{{ item['id'] }}">
                        <button type="submit" class="restore-btn" title="Восстановить">←</button>
                    </form>
                </li>
            {% else %}
                <li>История пуста</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
'''

templates = {
    'index.html': index_html,
    'scan.html': scan_html,
    'new_product.html': new_product_html,
    'add_batch.html': add_batch_html,
    'history.html': history_html
}

def render_template(template_name, **context):
    return render_template_string(templates[template_name], **context)
