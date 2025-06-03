import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, g, jsonify, render_template_string

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'expiry.db')

# Подключение к существующей БД
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Очистка старых записей истории (сохраняем 3 месяца)
def clear_old_history():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM history WHERE removed_date < ?", (three_months_ago,))
        db.commit()

# Удаление товаров через месяц после истечения срока
def remove_expired():
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)  # Удаляем товары, срок которых истек месяц назад
    
    cursor.execute('''
        SELECT b.id, p.barcode, p.name, b.expiration_date
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE DATE(b.expiration_date) <= ?
    ''', (one_month_ago.strftime('%Y-%m-%d'),))
    expired = cursor.fetchall()

    for item in expired:
        # Проверяем, не добавлен ли уже этот товар в историю
        cursor.execute("SELECT id FROM history WHERE barcode = ? AND expiration_date = ?",
                      (item['barcode'], item['expiration_date']))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO history (barcode, product_name, expiration_date, removed_date) VALUES (?, ?, ?, ?)",
                          (item['barcode'], item['name'], item['expiration_date'], today.strftime('%Y-%m-%d')))
        cursor.execute("DELETE FROM batches WHERE id = ?", (item['id'],))
    db.commit()

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date()
    
    # Получаем товары с сортировкой по сроку годности
    cursor.execute('''
        SELECT p.name, p.barcode, b.expiration_date, b.added_date
        FROM batches b
        JOIN products p ON p.id = b.product_id
        ORDER BY b.expiration_date ASC
    ''')
    
    items = []
    for row in cursor.fetchall():
        exp_date = datetime.strptime(row['expiration_date'], "%Y-%m-%d").date()
        days_since_expiry = (today - exp_date).days
        
        # Рассчитываем дату удаления (через месяц после истечения срока)
        removal_date = exp_date + timedelta(days=30)
        days_until_removal = (removal_date - today).days if removal_date > today else 0
        
        items.append((
            row['name'], 
            row['barcode'], 
            row['expiration_date'],
            days_since_expiry,
            days_until_removal,
            removal_date.strftime('%Y-%m-%d')
        ))
    
    return render_template('index.html', items=items, today=today.strftime('%Y-%m-%d'))

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        barcode = request.form['barcode'].strip()
        name = request.form.get('name', '').strip()
        manufacture_date = request.form['manufacture_date']
        duration_value = int(request.form['duration_value'])
        duration_unit = request.form['duration_unit']

        try:
            db = get_db()
            cursor = db.cursor()
            
            # Проверяем существование товара
            cursor.execute('SELECT id, name FROM products WHERE barcode = ?', (barcode,))
            product = cursor.fetchone()
            
            # Если товар не найден - создаем новый
            if not product:
                cursor.execute('INSERT INTO products (barcode, name) VALUES (?, ?)', (barcode, name))
                product_id = cursor.lastrowid
            else:
                product_id = product['id']
            
            # Рассчитываем срок годности
            mfg_date = datetime.strptime(manufacture_date, "%Y-%m-%d")
            if duration_unit == 'days':
                expiry_date = mfg_date + timedelta(days=duration_value)
            elif duration_unit == 'months':
                expiry_date = mfg_date + timedelta(days=duration_value * 30)
            elif duration_unit == 'hours':
                expiry_date = mfg_date + timedelta(hours=duration_value)
                expiry_date = expiry_date.replace(hour=0, minute=0, second=0)
            
            # Добавляем партию
            cursor.execute('''
                INSERT INTO batches (product_id, expiration_date, added_date)
                VALUES (?, ?, ?)
            ''', (product_id, expiry_date.strftime("%Y-%m-%d"), manufacture_date))
            db.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return f"Ошибка при добавлении: {str(e)}"

    return render_template('scan.html')

@app.route('/get-product-name', methods=['GET'])
def get_product_name():
    barcode = request.args.get('barcode')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name FROM products WHERE barcode = ?', (barcode,))
    result = cursor.fetchone()
    if result:
        return jsonify({'found': True, 'name': result['name']})
    else:
        return jsonify({'found': False})

@app.route('/get-all-products', methods=['GET'])
def get_all_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT barcode, name FROM products')
    products = [dict(row) for row in cursor.fetchall()]
    return jsonify({'products': products})

@app.route('/new_product', methods=['GET', 'POST'])
def new_product():
    barcode = request.args.get('barcode')
    if request.method == 'POST':
        name = request.form['name']
        barcode = request.form['barcode']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO products (barcode, name) VALUES (?, ?)", (barcode, name))
        db.commit()
        return redirect(url_for('add_batch', barcode=barcode))
    return render_template('new_product.html', barcode=barcode)

@app.route('/add_batch', methods=['GET', 'POST'])
def add_batch():
    barcode = request.args.get('barcode')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM products WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()

    if not product:
        return "Товар не найден", 404

    if request.method == 'POST':
        expiration_date = request.form['expiration_date']
        cursor.execute("INSERT INTO batches (product_id, expiration_date) VALUES (?, ?)", 
                       (product['id'], expiration_date))
        db.commit()
        return redirect(url_for('index'))

    return render_template('add_batch.html', product_name=product['name'])

@app.route('/history')
def history():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM history ORDER BY removed_date DESC")
    history_items = cursor.fetchall()
    return render_template('history.html', history_items=history_items)

def run_app():
    with app.app_context():
        # Автоматическое удаление старых товаров и очистка истории
        remove_expired()
        clear_old_history()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# Шаблоны
templates = {
    'index.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Контроль сроков</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .item { padding: 10px; border-bottom: 1px solid #eee; }
        .expired { background-color: #ffdddd; }
        .soon { background-color: #ffffcc; }
        .to-remove { background-color: #ffcccc; }
    </style>
</head>
<body>
    <h1>Товары с истекающим сроком</h1>
    <a href="/scan">Сканировать новый товар</a> | 
    <a href="/history">История</a>
    <hr>
    {% for item in items %}
        {% set exp_date = item[2] %}
        {% set days_since_expiry = item[3] %}
        {% set days_until_removal = item[4] %}
        <div class="item 
            {% if days_since_expiry > 0 %}expired
            {% elif days_until_removal <= 7 %}soon
            {% endif %}">
            <strong>{{ item[0] }}</strong> ({{ item[1] }})<br>
            Годен до: {{ item[2] }}<br>
            Просрочено дней назад: {{ item[3] }}<br>
            Удалить через: {{ item[4] }} дней ({{ item[5] }})
        </div>
    {% else %}
        <p>Нет товаров с истекающим сроком</p>
    {% endfor %}
</body>
</html>
''',
    
    'scan.html': '''
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
        <video id="video" autoplay></video>
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

        Quagga.init({
            inputStream: {
                name: 'Live',
                type: 'LiveStream',
                target: video,
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
                showNotification("Ошибка камеры: " + err.message, 'error');
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
                        nameInput.readOnly = true;
                        showNotification("Товар найден: " + data.name, 'success');
                        if (successSound) successSound.play().catch(e => console.log("Audio error:", e));
                    } else {
                        nameInput.value = '';
                        nameInput.readOnly = false;
                        showNotification("Товар не найден", 'error');
                        if (errorSound) errorSound.play().catch(e => console.log("Audio error:", e));
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
                            nameInput.readOnly = true;
                        };
                        productList.appendChild(item);
                    }
                });
        }

        loadProducts();
    </script>
</body>
</html>
''',
    
    'new_product.html': '''
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
''',
    
    'add_batch.html': '''
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
''',
    
    'history.html': '''
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
}

def render_template(template_name, **context):
    return render_template_string(templates[template_name], **context)

if __name__ == '__main__':
    run_app()
