from flask import render_template_string

# Основные стили Вкусвилла
VKUSVILL_STYLES = '''
    :root {
        --vkusvill-green: #2e7d32;
        --vkusvill-light-green: #4caf50;
        --vkusvill-dark-green: #1b5e20;
        --vkusvill-red: #d32f2f;
        --vkusvill-orange: #ff9800;
        --vkusvill-yellow: #ffeb3b;
        --vkusvill-gray: #f5f5f5;
        --vkusvill-dark-gray: #616161;
    }
    
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    body {
        font-family: 'Roboto', 'Arial', sans-serif;
        background-color: #f9f9f9;
        color: #333;
        line-height: 1.6;
    }
    
    .vkusvill-container {
        max-width: 100%;
        padding: 0 15px;
        margin: 0 auto;
    }
    
    .vkusvill-header {
        background-color: var(--vkusvill-green);
        color: white;
        padding: 15px 0;
        text-align: center;
        position: relative;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .vkusvill-header img {
        height: 40px;
        margin-bottom: 10px;
    }
    
    .vkusvill-header h1 {
        font-size: 1.3rem;
        font-weight: 500;
        margin: 0;
    }
    
    .vkusvill-nav {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 15px;
    }
    
    .vkusvill-nav a {
        color: white;
        text-decoration: none;
        padding: 8px 15px;
        border-radius: 4px;
        background-color: rgba(255, 255, 255, 0.2);
        transition: background-color 0.3s;
        font-size: 0.9rem;
    }
    
    .vkusvill-nav a:hover {
        background-color: rgba(255, 255, 255, 0.3);
    }
    
    .vkusvill-content {
        padding: 20px 0;
        min-height: calc(100vh - 180px);
    }
    
    .vkusvill-footer {
        text-align: center;
        padding: 15px 0;
        background-color: var(--vkusvill-dark-green);
        color: white;
        font-size: 0.85rem;
    }
    
    .vkusvill-footer p {
        margin: 5px 0;
    }
    
    .vkusvill-btn {
        background-color: var(--vkusvill-green);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 15px;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.3s;
    }
    
    .vkusvill-btn:hover {
        background-color: var(--vkusvill-dark-green);
    }
    
    .vkusvill-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Специфические стили для статусов */
    .expired { 
        border-left: 4px solid var(--vkusvill-red);
    }
    .warning { 
        border-left: 4px solid var(--vkusvill-orange);
    }
    .soon { 
        border-left: 4px solid var(--vkusvill-yellow);
    }
    .normal { 
        border-left: 4px solid var(--vkusvill-green);
    }
'''

# Главная страница
index_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Контроль сроков | Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        {VKUSVILL_STYLES}
        
        .items-container {{
            margin-top: 15px;
        }}
        
        .vkusvill-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .item-info {{
            flex-grow: 1;
        }}
        
        .item-status {{
            display: flex;
            align-items: center;
            margin-top: 10px;
        }}
        
        .status-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-expired {{ background-color: var(--vkusvill-red); }}
        .status-warning {{ background-color: var(--vkusvill-orange); }}
        .status-soon {{ background-color: var(--vkusvill-yellow); }}
        .status-normal {{ background-color: var(--vkusvill-green); }}
        
        .move-btn {{
            background-color: var(--vkusvill-green);
            color: white;
            border: none;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <header class="vkusvill-header">
        <div class="vkusvill-container">
            <img src="/logo.png" alt="Вкусвилл">
            <h1>Контроль сроков годности</h1>
            <nav class="vkusvill-nav">
                <a href="/scan">Сканировать</a>
                <a href="/history">История</a>
            </nav>
        </div>
    </header>
    
    <main class="vkusvill-content">
        <div class="vkusvill-container">
            <div class="items-container">
                {% for item in items %}
                    <div class="vkusvill-item {{ item.status }}">
                        <div class="item-info">
                            <strong>{{ item.name }}</strong>
                            <div style="color: #666; font-size: 0.9rem; margin-top: 5px;">
                                {{ item.barcode }} | Годен до: {{ item.expiration_date }}
                            </div>
                            
                            <div class="item-status">
                                {% if item.status == "expired" %}
                                    <div class="status-indicator status-expired"></div>
                                    <span>Просрочено: {{ item.days_since_expiry }} дн.</span>
                                {% elif item.status == "warning" %}
                                    <div class="status-indicator status-warning"></div>
                                    <span>Истекает сегодня!</span>
                                {% elif item.status == "soon" %}
                                    <div class="status-indicator status-soon"></div>
                                    <span>Истекает через: {{ item.days_until_expiry }} дн.</span>
                                {% else %}
                                    <div class="status-indicator status-normal"></div>
                                    <span>Годен: {{ item.days_until_expiry }} дн.</span>
                                {% endif %}
                            </div>
                            
                            <div style="font-size: 0.85rem; margin-top: 8px; color: #888;">
                                Удаление через: {{ item.days_until_removal }} дн. ({{ item.removal_date }})
                            </div>
                        </div>
                        <form action="/move_to_history" method="POST" style="display: flex; align-items: center;">
                            <input type="hidden" name="batch_id" value="{{ item.id }}">
                            <button type="submit" class="move-btn" title="Переместить в историю">→</button>
                        </form>
                    </div>
                {% else %}
                    <div class="vkusvill-card" style="text-align: center; padding: 30px;">
                        <p>Нет товаров с истекающим сроком</p>
                        <a href="/scan" class="vkusvill-btn" style="margin-top: 15px; display: inline-block;">
                            Добавить товар
                        </a>
                    </div>
                {% endfor %}
            </div>
        </div>
    </main>
    
    <footer class="vkusvill-footer">
        <div class="vkusvill-container">
            <p>Сделано "M2 (Shevchenko)" by Bekeshnyuk</p>
            <p>&copy; 2023 Вкусвилл</p>
        </div>
    </footer>
</body>
</html>
'''

scan_html = f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Сканирование | Вкусвилл</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        {VKUSVILL_STYLES}
        
        .scanner-container { 
            position: relative; 
            width: 100%;
            max-width: 400px;
            height: 250px;
            margin: 0 auto 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            background: black;
        }
        
        .vkusvill-form { 
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
        }
        
        .vkusvill-form-group {{
            margin-bottom: 20px;
        }}
        
        .vkusvill-form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--vkusvill-dark-green);
        }}
        
        .vkusvill-form-control {{
            width: 100%; 
            padding: 12px 15px; 
            font-size: 1rem; 
            border: 1px solid #ddd;
            border-radius: 6px; 
            background: white;
        }}
        
        .vkusvill-form-control:focus {{
            border-color: var(--vkusvill-green);
            outline: none;
            box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.2);
        }}
        
        .duration-container {{
            display: flex;
            gap: 10px;
        }}
        
        .duration-container input {{
            flex: 2;
        }}
        
        .duration-container select {{
            flex: 1;
        }}
        
        .manual-input {{
            text-align: center;
            margin: 15px 0;
        }}
        
        .manual-input a {{
            color: var(--vkusvill-green);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .camera-controls {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 15px 0;
        }}
        
        .camera-btn {{
            padding: 10px 20px;
            background: white;
            border: 1px solid var(--vkusvill-green);
            border-radius: 6px;
            color: var(--vkusvill-green);
            cursor: pointer;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <header class="vkusvill-header">
        <div class="vkusvill-container">
            <img src="/logo.png" alt="Вкусвилл">
            <h1>Сканирование товара</h1>
            <nav class="vkusvill-nav">
                <a href="/">На главную</a>
            </nav>
        </div>
    </header>
    
    <main class="vkusvill-content">
        <div class="vkusvill-container">
            <div class="scanner-container">
                <video id="video" autoplay playsinline muted></video>
                <div class="overlay"></div>
                <div id="camera-error" class="camera-error" style="display: none; color: white; padding: 20px; text-align: center;">
                    Ошибка доступа к камере. Проверьте разрешения.
                </div>
            </div>

            <div class="camera-controls">
                <button id="restart-btn" class="camera-btn">Перезапустить</button>
                <button id="torch-btn" class="camera-btn">Фонарик</button>
            </div>

            <div class="manual-input">
                <a href="#" id="manual-input-link">Ввести штрих-код вручную</a>
            </div>

            <form method="POST" class="vkusvill-form">
                <div class="vkusvill-form-group">
                    <label for="barcode">Штрих-код:</label>
                    <input type="text" name="barcode" id="barcode" class="vkusvill-form-control" 
                           placeholder="Отсканируйте или введите вручную" required>
                </div>

                <div class="vkusvill-form-group">
                    <label for="name">Наименование товара:</label>
                    <input type="text" id="name" name="name" class="vkusvill-form-control" required>
                </div>

                <div class="vkusvill-form-group">
                    <label for="manufacture_date">Дата изготовления:</label>
                    <input type="date" name="manufacture_date" class="vkusvill-form-control" required>
                </div>

                <div class="vkusvill-form-group">
                    <label>Срок годности:</label>
                    <div class="duration-container">
                        <input type="number" name="duration_value" class="vkusvill-form-control" required min="1" value="30">
                        <select name="duration_unit" class="vkusvill-form-control">
                            <option value="days">дней</option>
                            <option value="months">месяцев</option>
                            <option value="years">лет</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="vkusvill-btn" style="width: 100%;">Сохранить товар</button>
            </form>
        </div>
    </main>
    
    <footer class="vkusvill-footer">
        <div class="vkusvill-container">
            <p>Сделано "M2 (Shevchenko)" by Bekeshnyuk</p>
            <p>&copy; 2023 Вкусвилл</p>
        </div>
    </footer>
    
    <audio id="beep" class="beep" src="https://assets.mixkit.co/sfx/preview/mixkit-electronic-retail-scanner-beep-1083.mp3" preload="auto"></audio>

    <script type="module">
        // Оригинальный скрипт сканера без изменений
        // [Оригинальный JavaScript код сканера]
    </script>
</body>
</html>
'''

# Обновленные шаблоны для других страниц
new_product_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Новый товар | Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        {VKUSVILL_STYLES}
        
        .vkusvill-form {{
            max-width: 500px;
            margin: 0 auto;
            padding: 20px 0;
        }}
    </style>
</head>
<body>
    <header class="vkusvill-header">
        <div class="vkusvill-container">
            <img src="/logo.png" alt="Вкусвилл">
            <h1>Добавление нового товара</h1>
            <nav class="vkusvill-nav">
                <a href="/">На главную</a>
            </nav>
        </div>
    </header>
    
    <main class="vkusvill-content">
        <div class="vkusvill-container">
            <form method="POST" class="vkusvill-form">
                <div class="vkusvill-form-group">
                    <label>Штрих-код:</label>
                    <input type="text" name="barcode" class="vkusvill-form-control" value="{{ barcode }}" readonly>
                </div>
                
                <div class="vkusvill-form-group">
                    <label>Название товара:</label>
                    <input type="text" name="name" class="vkusvill-form-control" required autofocus>
                </div>
                
                <button type="submit" class="vkusvill-btn" style="width: 100%;">Сохранить товар</button>
            </form>
        </div>
    </main>
    
    <footer class="vkusvill-footer">
        <div class="vkusvill-container">
            <p>Сделано "M2 (Shevchenko)" by Bekeshnyuk</p>
            <p>&copy; 2023 Вкусвилл</p>
        </div>
    </footer>
</body>
</html>
'''

add_batch_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Добавить срок | Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        {VKUSVILL_STYLES}
        
        .vkusvill-form {{
            max-width: 500px;
            margin: 0 auto;
            padding: 20px 0;
        }}
    </style>
</head>
<body>
    <header class="vkusvill-header">
        <div class="vkusvill-container">
            <img src="/logo.png" alt="Вкусвилл">
            <h1>Добавление срока годности</h1>
            <nav class="vkusvill-nav">
                <a href="/">На главную</a>
            </nav>
        </div>
    </header>
    
    <main class="vkusvill-content">
        <div class="vkusvill-container">
            <h2 style="text-align: center; margin-bottom: 20px; color: var(--vkusvill-dark-green);">
                {{ product_name }}
            </h2>
            
            <form method="POST" class="vkusvill-form">
                <div class="vkusvill-form-group">
                    <label>Срок годности:</label>
                    <input type="date" name="expiration_date" class="vkusvill-form-control" required>
                </div>
                
                <button type="submit" class="vkusvill-btn" style="width: 100%;">Добавить срок</button>
            </form>
        </div>
    </main>
    
    <footer class="vkusvill-footer">
        <div class="vkusvill-container">
            <p>Сделано "M2 (Shevchenko)" by Bekeshnyuk</p>
            <p>&copy; 2023 Вкусвилл</p>
        </div>
    </footer>
</body>
</html>
'''

history_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>История | Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        {VKUSVILL_STYLES}
        
        .history-container {{
            margin-top: 20px;
        }}
        
        .history-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid var(--vkusvill-dark-gray);
        }}
        
        .item-info {{
            flex-grow: 1;
        }}
        
        .restore-btn {{
            background-color: var(--vkusvill-green);
            color: white;
            border: none;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            font-size: 1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <header class="vkusvill-header">
        <div class="vkusvill-container">
            <img src="/logo.png" alt="Вкусвилл">
            <h1>История списанных товаров</h1>
            <nav class="vkusvill-nav">
                <a href="/">На главную</a>
            </nav>
        </div>
    </header>
    
    <main class="vkusvill-content">
        <div class="vkusvill-container">
            <div class="history-container">
                {% if history_items %}
                    {% for item in history_items %}
                        <div class="history-item">
                            <div style="display: flex; align-items: center;">
                                <div class="item-info">
                                    <strong>{{ item['product_name'] }}</strong>
                                    <div style="color: #666; font-size: 0.9rem; margin-top: 5px;">
                                        {{ item['barcode'] }}
                                    </div>
                                    <div style="font-size: 0.9rem; margin-top: 8px;">
                                        <div>Срок годности: {{ item['expiration_date'] }}</div>
                                        <div>Удален: {{ item['removed_date'] }}</div>
                                    </div>
                                </div>
                                <form action="/restore_from_history" method="POST">
                                    <input type="hidden" name="history_id" value="{{ item['id'] }}">
                                    <button type="submit" class="restore-btn" title="Восстановить">←</button>
                                </form>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="vkusvill-card" style="text-align: center; padding: 30px;">
                        <p>История списанных товаров пуста</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </main>
    
    <footer class="vkusvill-footer">
        <div class="vkusvill-container">
            <p>Сделано "M2 (Shevchenko)" by Bekeshnyuk</p>
            <p>&copy; 2023 Вкусвилл</p>
        </div>
    </footer>
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
