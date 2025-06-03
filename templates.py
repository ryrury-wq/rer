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
    <title>Сканирование</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .camera-container {
            position: relative;
            width: 100%;
            height: 20vh;
            overflow: hidden;
            border: 3px solid #ccc;
            margin-bottom: 20px;
            box-sizing: border-box;
        }
        video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .overlay {
            position: absolute;
            top: 3cm;
            left: 1cm;
            right: 1cm;
            bottom: 0;
            border: 2px dashed red;
            pointer-events: none;
        }
        .notification {
            padding: 10px;
            color: #fff;
            margin: 10px 0;
            display: none;
        }
        .success { background: #4caf50; }
        .error { background: #f44336; }
        .product-list {
            max-height: 300px;
            overflow-y: auto;
            border-top: 1px solid #ccc;
            padding-top: 10px;
        }
        .product-item {
            padding: 5px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        .product-item:hover {
            background: #f0f0f0;
        }
    </style>
</head>
<body>
    <h1>Сканирование товара</h1>

    <div class="camera-container">
        <video id="video" autoplay playsinline></video>
        <div class="overlay"></div>
    </div>

    <div class="notification" id="notification"></div>

    <form method="POST">
        <label>Штрих-код:</label><br>
        <input type="text" name="barcode" id="barcode" required autofocus><br><br>

        <label>Наименование:</label><br>
        <input type="text" id="name" name="name" required><br><br>

        <label>Дата изготовления:</label><br>
        <input type="date" name="manufacture_date" required><br><br>

        <label>Срок годности:</label><br>
        <input type="number" name="duration_value" required>
        <select name="duration_unit">
            <option value="days">дней</option>
            <option value="months">месяцев</option>
            <option value="hours">часов</option>
        </select><br><br>

        <button type="submit">Сохранить</button>
    </form>

    <h2>Справочник позиций</h2>
    <div class="product-list" id="productList"></div>

    <audio id="successSound" src="https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg"></audio>
    <audio id="errorSound" src="https://actions.google.com/sounds/v1/cartoon/cartoon_boing.ogg"></audio>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
    <script>
        const video = document.getElementById('video');
        const barcodeInput = document.getElementById('barcode');
        const nameInput = document.getElementById('name');
        const notification = document.getElementById('notification');
        const successSound = document.getElementById('successSound');
        const errorSound = document.getElementById('errorSound');
        const productList = document.getElementById('productList');

        function showNotification(message, type) {
            notification.className = `notification ${type}`;
            notification.textContent = message;
            notification.style.display = 'block';
            setTimeout(() => notification.style.display = 'none', 3000);
        }

        // Запуск камеры через Quagga
        Quagga.init({
            inputStream: {
                name: 'Live',
                type: 'LiveStream',
                target: video,  // сюда выводим видео
                constraints: {
                    facingMode: 'environment'
                },
            },
            decoder: {
                readers: ['ean_reader', 'code_128_reader']
            },
        }, function(err) {
            if (err) { 
                console.log(err); 
                showNotification('Ошибка инициализации камеры', 'error');
                return; 
            }
            Quagga.start();
        });

        Quagga.onDetected(function(data) {
            const code = data.codeResult.code;
            barcodeInput.value = code;
            fetch(`/get-product-name?barcode=${code}`)
                .then(res => res.json())
                .then(data => {
                    if (data.found) {
                        nameInput.value = data.name;
                        showNotification("Товар найден: " + data.name, 'success');
                        successSound.play();
                    } else {
                        nameInput.value = '';
                        showNotification("Товар не найден", 'error');
                        errorSound.play();
                    }
                });
            Quagga.stop();
        });

        function loadProducts() {
            fetch('/get-all-products')
                .then(res => res.json())
                .then(data => {
                    const sorted = data.products.sort((a, b) => a.name.localeCompare(b.name));
                    productList.innerHTML = '';
                    for (const p of sorted) {
                        const item = document.createElement('div');
                        item.className = 'product-item';
                        item.textContent = `${p.name} (${p.barcode})`;
                        item.onclick = () => {
                            barcodeInput.value = p.barcode;
                            nameInput.value = p.name;
                        };
                        productList.appendChild(item);
                    }
                });
        }

        loadProducts();
    </script>
</body>
</html>



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
