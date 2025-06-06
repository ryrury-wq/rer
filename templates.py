from flask import render_template_string

# Главная страница
index_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Контроль сроков</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .item { padding: 10px; border-bottom: 1px solid #eee; }
        .expired { background-color: #ffdddd; }
        .soon { background-color: #ffffcc; }
    </style>
</head>
<body>
    <h1>Товары с истекающим сроком</h1>
    <a href="/scan">Сканировать новый товар</a> | 
    <a href="/history">История</a>
    <hr>
    {% for item in items %}
        <div class="item 
            {% if item.days_since_expiry > 0 %}expired
            {% elif item.days_until_expiry <= 7 %}soon
            {% endif %}">
            <strong>{{ item.name }}</strong> ({{ item.barcode }})<br>
            Годен до: {{ item.expiration_date }}<br>
            
            {% if item.days_since_expiry > 0 %}
                Просрочено дней назад: {{ item.days_since_expiry }}
                <br>Удаление через: {{ item.days_until_removal }} дней
            {% else %}
                До истечения: {{ item.days_until_expiry }} дней
                <br>Удаление через: {{ item.days_until_removal }} дней ({{ item.removal_date }})
            {% endif %}
        </div>
    {% else %}
        <p>Нет товаров с истекающим сроком</p>
    {% endfor %}
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
        body { font-family: sans-serif; padding: 1em; margin: 0; background: #f9f9f9; }
        .scanner-container { position: relative; width: 100%; max-width: 600px; margin: 0 auto; }
        video { width: 100%; height: auto; border-radius: 10px; }
        .overlay { position: absolute; top: 30%; left: 10%; width: 80%; height: 20%; 
                  border: 2px dashed red; border-radius: 8px; pointer-events: none; }
        form { margin-top: 20px; }
        input[type="text"], input[type="date"], input[type="number"], select {
            width: 100%; padding: 12px; font-size: 1em; border: 1px solid #ccc;
            border-radius: 4px; margin-bottom: 10px; background: #fff; }
        button { width: 100%; padding: 12px; background-color: #28a745; color: white;
                font-size: 1.1em; border: none; border-radius: 4px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Сканирование товара</h1>

    <div class="scanner-container">
        <video id="video" autoplay playsinline></video>
        <div class="overlay"></div>
    </div>

    <form method="POST">
        <div class="form-group">
            <label for="barcode">Штрих-код:</label>
            <input type="text" name="barcode" id="barcode" readonly placeholder="Ожидание сканирования..." required>
        </div>

        <div class="form-group">
            <label for="name">Наименование:</label>
            <input type="text" id="name" name="name" required>
        </div>

        <div class="form-group">
            <label for="manufacture_date">Дата изготовления:</label>
            <input type="date" name="manufacture_date" required>
        </div>

        <div class="form-group">
            <label>Срок годности:</label>
            <div style="display: flex; gap: 10px;">
                <input type="number" name="duration_value" required style="flex: 2;">
                <select name="duration_unit" style="flex: 1;">
                    <option value="days">дней</option>
                    <option value="months">месяцев</option>
                </select>
            </div>
        </div>

        <button type="submit">Сохранить</button>
    </form>

    <script type="module">
        import { BrowserMultiFormatReader } from 'https://cdn.jsdelivr.net/npm/@zxing/browser@0.0.10/+esm';

        const codeReader = new BrowserMultiFormatReader();
        const video = document.getElementById('video');
        const barcodeInput = document.getElementById('barcode');

        codeReader.decodeFromVideoDevice(null, video, (result, err) => {
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
        ul { list-style-type: none; padding: 0; }
        li { padding: 8px; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <h1>История списанных товаров</h1>
    <a href="/">На главную</a>
    <hr>
    <ul>
        {% for item in history_items %}
            <li>
                <strong>{{ item['product_name'] }}</strong> ({{ item['barcode'] }})<br>
                Срок годности: {{ item['expiration_date'] }}<br>
                Удален: {{ item['removed_date'] }}
            </li>
        {% else %}
            <li>История пуста</li>
        {% endfor %}
    </ul>
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
