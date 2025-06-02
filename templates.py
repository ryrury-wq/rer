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
        {% set exp_date = item[2] %}
        <div class="item 
            {% if exp_date < today %}expired
            {% elif exp_date == today %}soon
            {% endif %}">
            {{ item[1] }} ({{ item[0] }}) - Годен до: {{ exp_date }}
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
<html>
<head>
    <meta charset="utf-8">
    <title>Сканирование и справочник</title>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        #camera-container {
            width: 100%;
            height: 20vh; /* 1/5 экрана */
            background: #000;
        }
        #reader {
            width: 100%;
            height: 100%;
        }
        #manual-form {
            padding: 10px;
            background: #f8f8f8;
        }
        input[type="text"] {
            padding: 8px;
            width: 70%;
            font-size: 1em;
        }
        button {
            padding: 8px 15px;
            font-size: 1em;
        }
        #product-list {
            padding: 10px;
        }
        .product {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
    </style>
</head>
<body>

<div id="camera-container">
    <div id="reader"></div>
</div>

<div id="manual-form">
    <form method="POST" id="scan-form">
        <input type="text" name="barcode" id="barcode-input" placeholder="Введите штрихкод вручную" required>
        <button type="submit">Добавить</button>
    </form>
</div>

<div id="product-list">
    <h2>Справочник товаров</h2>
    {% for item in items %}
        <div class="product">
            <div>{{ item['name'] }}</div>
            <div>{{ item['barcode'] }}</div>
        </div>
    {% else %}
        <p>Нет добавленных товаров</p>
    {% endfor %}
</div>

<script>
    function onScanSuccess(decodedText, decodedResult) {
        // Поместить штрихкод и отправить форму
        document.getElementById('barcode-input').value = decodedText;
        document.getElementById('scan-form').submit();
    }

    function onScanError(errorMessage) {
        // Можно логировать ошибки при необходимости
    }

    const html5QrCode = new Html5Qrcode("reader");

    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
            let cameraId = devices[0].id;
            html5QrCode.start(
                cameraId,
                {
                    fps: 10,
                    qrbox: { width: 300, height: 80 }, // Только горизонтальная зона
                },
                onScanSuccess,
                onScanError
            );
        }
    }).catch(err => {
        console.error("Ошибка получения камеры:", err);
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
</head>
<body>
    <h1>Добавление нового товара</h1>
    <form method="POST">
        Штрих-код: <input type="text" name="barcode" value="{{ barcode }}" readonly><br>
        Название товара: <input type="text" name="name" required><br>
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
</head>
<body>
    <h1>Добавление срока годности для: {{ product_name }}</h1>
    <form method="POST">
        Срок годности: <input type="date" name="expiration_date" required><br>
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
</head>
<body>
    <h1>История списанных товаров</h1>
    <a href="/">На главную</a>
    <hr>
    <ul>
        {% for item in history_items %}
            <li>{{ item[2] }} ({{ item[1] }}) - Срок: {{ item[3] }} | Удален: {{ item[4] }}</li>
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