from flask import render_template_string

# Главная страница
index_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Контроль сроков</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .items-container {
            max-height: 70vh;
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
        .move-btn:hover {
            background-color: #f0f0f0;
        }
        .expired { background-color: #ffdddd; }
        .warning { background-color: #ffcc99; } /* Оранжевый для 1 дня */
        .soon { background-color: #ffffcc; }
        .normal { background-color: white; }
    </style>
</head>
<body>
    <h1>Товары с истекающим сроком</h1>
    <a href="/scan">Сканировать новый товар</a> | 
    <a href="/history">История</a>
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

# Сканирование
scan_html = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Сканирование</title>
    <style>
        body { 
            font-family: sans-serif; 
            padding: 1em; 
            margin: 0; 
            background: #f9f9f9; 
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .scanner-container { 
            position: relative; 
            width: 80%; 
            max-width: 400px; /* Уменьшаем максимальную ширину */
            height: 200px; /* Фиксированная высота */
            margin: 0 auto;
            border-radius: 10px;
            overflow: hidden; /* Обрезаем видео по границам контейнера */
        }
        video { 
            width: 100%; 
            height: 100%; 
            object-fit: cover; /* Сохраняем пропорции видео */
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
            width: 80%;
            max-width: 400px;
            margin-top: 20px; 
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
        }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        .scanner-instruction {
            text-align: center;
            margin: 10px 0;
            font-size: 0.9em;
            color: #666;
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
        <!-- Остальная форма без изменений -->
    </form>

    <script type="module">
        import { BrowserMultiFormatReader } from 'https://cdn.jsdelivr.net/npm/@zxing/browser@0.0.10/+esm';

        const codeReader = new BrowserMultiFormatReader();
        const video = document.getElementById('video');
        const barcodeInput = document.getElementById('barcode');
        
        // Получаем доступ к камере с ограниченным разрешением
        const constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: "environment"
            }
        };

        // Запускаем сканер с ограничениями
        codeReader.decodeFromConstraints(
            constraints, 
            video, 
            (result, err) => {
                if (result) {
                    barcodeInput.value = result.getText();
                    
                    // Проверка наличия товара в базе
                    fetch(`/get-product-name?barcode=${result.getText()}`)
                        .then(res => res.json())
                        .then(data => {
                            if (data.found) {
                                document.getElementById('name').value = data.name;
                            }
                        });
                    
                    codeReader.reset();
                }
            }
        ).catch(err => {
            console.error(err);
            alert('Ошибка доступа к камере. Проверьте разрешения.');
        });
    </script>
</body>
</html>
'''

# Новый товар
new_product_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Новый товар</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        input, button { padding: 8px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Добавление нового товара</h1>
    <form method="POST">
        <label>Штрих-код:</label><br>
        <input type="text" name="barcode" value="{{ barcode }}" readonly><br>
        <label>Название товара:</label><br>
        <input type="text" name="name" required><br>
        <button type="submit">Сохранить</button>
    </form>
</body>
</html>
'''

# Добавление срока
add_batch_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Добавить срок</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        input, button { padding: 8px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Добавление срока годности для: {{ product_name }}</h1>
    <form method="POST">
        <label>Срок годности:</label><br>
        <input type="date" name="expiration_date" required><br>
        <button type="submit">Добавить</button>
    </form>
</body>
</html>
'''

# История
history_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>История</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
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
        .restore-btn:hover {
            background-color: #f0f0f0;
        }
    </style>
</head>
<body>
    <h1>История списанных товаров</h1>
    <a href="/">На главную</a>
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
