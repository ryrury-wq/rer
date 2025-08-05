import os
import psycopg2
import subprocess
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, g, jsonify, render_template, send_from_directory, make_response
from psycopg2.extras import DictCursor
from dateutil.relativedelta import relativedelta
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Словарь для преобразования кода магазина в суффикс таблиц
STORE_SUFFIX_MAP = {
    'm1': '_m1',
    'm2': '',  # Для основного магазина (М2 Шевченко) суффикс пустой
    'm3': '_m3',
    'm5': '_m5',
    'm6': '_m6'
}

# Подключение к PostgreSQL (общее для всех магазинов)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(
            os.environ['DATABASE_URL'],
            cursor_factory=DictCursor
        )
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Middleware для установки магазина
@app.before_request
def set_store_suffix():
    # Для статики и выбора магазина не нужен суффикс
    if request.endpoint in ['static', 'select_store', 'set_store']:
        return
    
    store_code = request.cookies.get('store_code')
    
    if not store_code:
        return redirect(url_for('select_store'))
    
    suffix = STORE_SUFFIX_MAP.get(store_code)
    if suffix is None:
        return redirect(url_for('select_store'))
    
    g.store_suffix = suffix

# Маршрут для выбора магазина
@app.route('/select_store', methods=['GET', 'POST'])
def select_store():
    if request.method == 'POST':
        store_code = request.form['store_code']
        if store_code not in STORE_SUFFIX_MAP:
            return "Неверный код магазина", 400
        
        response = make_response(redirect(url_for('index')))
        response.set_cookie('store_code', store_code, max_age=60*60*24*30)  # 30 дней
        return response
    
    # GET запрос - показать форму выбора
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT store_code, store_name FROM store_settings WHERE is_active = TRUE")
    stores = cursor.fetchall()
    
    # Возвращаем HTML напрямую
    return f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Выберите магазин ВкусВилл</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            /* Стили остаются без изменений */
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Open Sans', Arial, sans-serif;
                background: linear-gradient(135deg, #f8fff0 0%, #e8f5e9 100%);
                color: #2c3e50;
                min-height: 100vh;
                padding: 20px;
                position: relative;
                overflow-x: hidden;
            }}
            
            /* ... (остальные стили без изменений) ... */
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">
                    <div class="logo-icon">
                        <i class="fas fa-store"></i>
                    </div>
                    <div class="logo-text">ВкусВилл</div>
                </div>
                <p class="subtitle">Выберите ваш любимый магазин для продолжения</p>
            </div>
            
            <div class="content">
                <h1 class="title">Выберите магазин</h1>
                
                <form method="post" action="/select_store">
                    <div class="radio-group">
                        {"".join([f'''
                        <label>
                            <input class="store-radio" type="radio" name="store_code" value="{store['store_code']}">
                            <div class="store-card">
                                <div class="store-icon">
                                    <i class="fas fa-shopping-basket"></i>
                                </div>
                                <div class="store-info">
                                    <div class="store-name">{store['store_name']}</div>
                                    <div class="store-address">Адрес: уточняется</div>
                                    <div class="store-hours">
                                        <i class="fas fa-clock"></i>
                                        <span>08:00 - 23:00</span>
                                    </div>
                                </div>
                                <div class="store-distance">
                                    <i class="fas fa-location-dot"></i>
                                    <span>0.8 км</span>
                                </div>
                            </div>
                        </label>
                        ''' for store in stores])}
                    </div>
                    
                    <div class="button-container">
                        <button type="submit">
                            <i class="fas fa-arrow-right"></i>
                            Продолжить
                        </button>
                    </div>
                </form>
                
                <div class="features">
                    <div class="feature">
                        <i class="fas fa-apple-alt"></i>
                        <span>Свежие фермерские продукты</span>
                    </div>
                    <div class="feature">
                        <i class="fas fa-recycle"></i>
                        <span>Экологичная упаковка</span>
                    </div>
                    <div class="feature">
                        <i class="fas fa-truck"></i>
                        <span>Быстрая доставка</span>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2023 ВкусВилл — фермерские продукты с любовью</p>
                <p>Телефон поддержки: 8 (800) 555-35-35</p>
            </div>
        </div>
    </body>
    </html>
    '''

# Маршрут для установки магазина (API)
@app.route('/set_store', methods=['POST'])
def set_store():
    store_code = request.json.get('store_code')
    if not store_code or store_code not in STORE_SUFFIX_MAP:
        return jsonify({"error": "Invalid store code"}), 400
    
    response = jsonify({"success": True})
    response.set_cookie('store_code', store_code, max_age=60*60*24*30)
    return response

# Главная страница
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date()

    from_date_raw = request.args.get('from_date', '').strip()
    to_date_raw = request.args.get('to_date', '').strip()
    days_left = request.args.get('days_left', '').strip()

    def parse_date_russian(date_str):
        try:
            return datetime.strptime(date_str, '%d.%m.%Y').date()
        except:
            return None

    from_date = parse_date_russian(from_date_raw)
    to_date = parse_date_russian(to_date_raw)

    query = f'''
        SELECT b.id, p.name, p.barcode, b.expiration_date, b.added_date
        FROM batches{g.store_suffix} b
        JOIN products{g.store_suffix} p ON p.id = b.product_id
    '''
    filters = []
    params = []

    if from_date:
        filters.append("b.expiration_date >= %s")
        params.append(from_date.strftime('%Y-%m-%d'))

    if to_date:
        filters.append("b.expiration_date <= %s")
        params.append(to_date.strftime('%Y-%m-%d'))

    if days_left.isdigit():
        max_days = int(days_left)
        target_date = today + timedelta(days=max_days)
        filters.append("b.expiration_date <= %s")
        params.append(target_date.strftime('%Y-%m-%d'))

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY b.expiration_date ASC"
    cursor.execute(query, tuple(params))

    items = []
    for row in cursor.fetchall():
        exp_date = datetime.strptime(row['expiration_date'], "%Y-%m-%d").date()
        days_until_expiry = (exp_date - today).days
        days_since_expiry = max(0, (today - exp_date).days)
        removal_date = exp_date + timedelta(days=30)
        days_until_removal = max(0, (removal_date - today).days)

        if days_until_expiry <= 0:
            status = 'expired'
        elif days_until_expiry == 1:
            status = 'warning'
        elif days_until_expiry <= 5:
            status = 'soon'
        else:
            status = 'normal'

        items.append({
            'id': row['id'],
            'name': row['name'],
            'barcode': row['barcode'],
            'expiration_date': exp_date.strftime('%d.%m.%Y'),
            'days_until_expiry': days_until_expiry,
            'days_since_expiry': days_since_expiry,
            'removal_date': removal_date.strftime('%d.%m.%Y'),
            'days_until_removal': days_until_removal,
            'status': status
        })

    return render_template('index.html', items=items,
                           from_date=from_date_raw, to_date=to_date_raw)


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Получаем данные из формы
            barcode = request.form.get('barcode', '').strip()
            name = request.form.get('name', '').strip()
            manufacture_date = request.form.get('manufacture_date', '').strip()
            duration_value = request.form.get('duration_value', '0').strip()
            duration_unit = request.form.get('duration_unit', 'days').strip()

            # Валидация данных
            if not all([barcode, name, manufacture_date, duration_value]):
                return "Не все обязательные поля заполнены", 400

            try:
                duration_value = int(duration_value)
                if duration_value <= 0:
                    return "Срок годности должен быть положительным числом", 400
            except ValueError:
                return "Некорректное значение срока годности", 400

            try:
                m_date = datetime.strptime(manufacture_date, '%Y-%m-%d').date()
            except ValueError:
                return "Неверный формат даты. Используйте YYYY-MM-DD", 400

            # Вычисляем дату истечения срока
            if duration_unit == 'days':
                exp_date = m_date + timedelta(days=duration_value)
            elif duration_unit == 'months':
                exp_date = m_date + relativedelta(months=duration_value)
            elif duration_unit == 'years':
                exp_date = m_date + relativedelta(years=duration_value)
            elif duration_unit == 'hours':
                exp_date = m_date + timedelta(hours=duration_value)
            else:
                exp_date = m_date + timedelta(days=30)

            exp_date_str = exp_date.strftime('%Y-%m-%d')

            # Проверяем/добавляем продукт
            cursor.execute(f"SELECT id FROM products{g.store_suffix} WHERE barcode = %s", (barcode,))
            product = cursor.fetchone()

            if not product:
                cursor.execute(
                    f"INSERT INTO products{g.store_suffix} (barcode, name) VALUES (%s, %s) RETURNING id", 
                    (barcode, name)
                )
                product_id = cursor.fetchone()['id']
            else:
                product_id = product['id']

            # Проверка на дубликат партии
            cursor.execute(f"""
                SELECT 1 FROM batches{g.store_suffix} 
                WHERE product_id = %s AND expiration_date = %s
            """, (product_id, exp_date_str))
            
            if cursor.fetchone():
                db.rollback()
                return "Такая партия уже существует", 400

            # Добавляем новую партию
            cursor.execute(f"""
                INSERT INTO batches{g.store_suffix} (product_id, expiration_date) 
                VALUES (%s, %s)
            """, (product_id, exp_date_str))
            
            db.commit()
            return redirect(url_for('index'))

        except Exception as e:
            db.rollback()
            app.logger.error(f"Scan POST Error: {str(e)}")
            return f"Server Error: {str(e)}", 500
    
    # GET-запрос - отображаем форму сканирования
    return render_template('scan.html')

@app.route('/get-product-name', methods=['GET'])
def get_product_name():
    barcode = request.args.get('barcode')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'SELECT name FROM products{g.store_suffix} WHERE barcode = %s', (barcode,))
    result = cursor.fetchone()
    if result:
        return jsonify({'found': True, 'name': result['name']})
    else:
        return jsonify({'found': False})

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/get-all-products', methods=['GET'])
def get_all_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'SELECT barcode, name FROM products{g.store_suffix}')
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
        cursor.execute(f"INSERT INTO products{g.store_suffix} (barcode, name) VALUES (?, ?)", (barcode, name))
        db.commit()
        return redirect(url_for('add_batch', barcode=barcode))
    return render_template('new_product.html', barcode=barcode)

@app.route('/add_batch', methods=['GET', 'POST'])
def add_batch():
    if request.method == 'GET':
        # Обработка GET-запроса (показ формы)
        barcode = request.args.get('barcode')
        if not barcode:
            return redirect(url_for('assortment'))
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT name FROM products{g.store_suffix} WHERE barcode = %s", (barcode,))
        product = cursor.fetchone()
        
        if not product:
            return redirect(url_for('assortment'))
            
        return render_template('add_batch.html', 
                             product_name=product['name'],
                             barcode=barcode)

    # Обработка POST-запроса (добавление данных)
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Получаем и валидируем данные
        barcode = request.form.get('barcode', '').strip()
        manufacture_date = request.form.get('manufacture_date', '').strip()
        duration_value = request.form.get('duration_value', '').strip()
        duration_unit = request.form.get('duration_unit', 'days').strip()
        expiration_date = request.form.get('expiration_date', '').strip()

        # Проверка обязательных полей
        if not barcode:
            return "Не указан штрих-код товара", 400

        # Получаем информацию о продукте
        cursor.execute(f"SELECT id FROM products{g.store_suffix} WHERE barcode = %s", (barcode,))
        product = cursor.fetchone()
        if not product:
            return "Товар с таким штрих-кодом не найден", 404

        # Определяем дату истечения срока
        if manufacture_date and duration_value:
            try:
                m_date = datetime.strptime(manufacture_date, '%Y-%m-%d').date()
                duration = int(duration_value)
                if duration <= 0:
                    return "Срок годности должен быть положительным числом", 400

                if duration_unit == 'days':
                    exp_date = m_date + timedelta(days=duration)
                elif duration_unit == 'months':
                    exp_date = m_date + relativedelta(months=duration)
                elif duration_unit == 'years':
                    exp_date = m_date + relativedelta(years=duration)
                else:
                    exp_date = m_date + timedelta(days=30)

                expiration_date = exp_date.strftime('%Y-%m-%d')
            except ValueError as e:
                return f"Некорректные данные: {str(e)}", 400
        elif expiration_date:
            try:
                # Проверяем формат даты, если указана напрямую
                datetime.strptime(expiration_date, '%Y-%m-%d')
            except ValueError:
                return "Неверный формат даты. Используйте YYYY-MM-DD", 400
        else:
            return "Не указаны данные о сроке годности", 400

        # Проверка на дубликат
        cursor.execute(f"""
            SELECT 1 FROM batches{g.store_suffix} 
            WHERE product_id = %s AND expiration_date = %s
        """, (product['id'], expiration_date))
        
        if cursor.fetchone():
            return "Такая партия уже существует", 400

        # Добавление новой партии
        cursor.execute(f"""
            INSERT INTO batches{g.store_suffix} (product_id, expiration_date) 
            VALUES (%s, %s)
        """, (product['id'], expiration_date))
        
        db.commit()
        return redirect(url_for('assortment'))

    except Exception as e:
        db.rollback()
        app.logger.error(f"Add batch error: {str(e)}")
        return f"Ошибка сервера: {str(e)}", 500

@app.route('/assortment')
def assortment():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT p.id, p.barcode, p.name, 
               (SELECT COUNT(*) FROM batches{g.store_suffix} b WHERE b.product_id = p.id) AS batch_count
        FROM products{g.store_suffix} p
        ORDER BY p.name
    ''')
    products = cursor.fetchall()
    return render_template('assortment.html', products=products)

@app.route('/history')
def history():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM history{g.store_suffix} ORDER BY removed_date DESC")
    history_items = cursor.fetchall()
    return render_template('history.html', history_items=history_items)

@app.route('/move_to_history', methods=['POST'])
def move_to_history():
    batch_id = int(request.form['batch_id'])  # Явное преобразование в int
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date().strftime('%Y-%m-%d')

    # Получаем информацию о товаре
    cursor.execute(f'''
    SELECT p.barcode, p.name, b.expiration_date
    FROM batches{g.store_suffix} b
    JOIN products{g.store_suffix} p ON b.product_id = p.id
    WHERE b.id = %s
''', (batch_id,)) 
    item = cursor.fetchone()

    if item:
        # Проверяем, нет ли уже такой записи в истории
        cursor.execute(f"SELECT id FROM history{g.store_suffix} WHERE barcode = %s AND expiration_date = %s",
                     (item['barcode'], item['expiration_date']))
        if not cursor.fetchone():
            # Добавляем в историю
            cursor.execute(f"INSERT INTO history{g.store_suffix} (barcode, product_name, expiration_date, removed_date) VALUES (%s, %s, %s, %s)",
                          (item['barcode'], item['name'], item['expiration_date'], today))

        # Удаляем из активных
        cursor.execute(f"DELETE FROM batches{g.store_suffix} WHERE id = %s", (batch_id,))
        db.commit()

    return redirect(url_for('index'))

@app.route('/restore_from_history', methods=['POST'])
def restore_from_history():
    history_id = request.form['history_id']
    db = get_db()
    cursor = db.cursor()
    
    # Получаем информацию из истории
    cursor.execute(f"SELECT * FROM history{g.store_suffix} WHERE id = %s", (history_id,))
    item = cursor.fetchone()
    
    if item:
        # Проверяем существование товара
        cursor.execute(f"SELECT id FROM products{g.store_suffix} WHERE barcode = %s", (item['barcode'],))
        product = cursor.fetchone()
        
        if not product:
            # Если товара нет, создаем новый
            cursor.execute(f"INSERT INTO products{g.store_suffix} (barcode, name) VALUES (%s, %s)", 
                          (item['barcode'], item['product_name']))
            product_id = cursor.lastrowid
        else:
            product_id = product['id']
        
        # Добавляем обратно в активные
        cursor.execute(f"INSERT INTO batches{g.store_suffix} (product_id, expiration_date) VALUES (%s, %s)", 
                      (product_id, item['expiration_date']))
        
        # Удаляем из истории
        cursor.execute(f"DELETE FROM history{g.store_suffix} WHERE id = %s", (history_id,))
        db.commit()
    
    return redirect(url_for('history'))

@app.route('/edit_batch', methods=['GET', 'POST'])
def edit_batch():
    batch_id = request.args.get('batch_id') if request.method == 'GET' else request.form['batch_id']
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        new_date = request.form['expiration_date']
        cursor.execute(f"UPDATE batches{g.store_suffix} SET expiration_date = %s WHERE id = %s", (new_date, batch_id))
        db.commit()
        return redirect(url_for('index'))
    
    cursor.execute(f"""
        SELECT b.id, b.expiration_date, p.name, p.barcode 
        FROM batches{g.store_suffix} b
        JOIN products{g.store_suffix} p ON b.product_id = p.id
        WHERE b.id = %s
    """, (batch_id,))
    batch = cursor.fetchone()
    
    return render_template('edit_batch.html', batch=batch)

@app.route('/delete_batch', methods=['POST'])
def delete_batch():
    batch_id = request.form['batch_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM batches{g.store_suffix} WHERE id = %s", (batch_id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/edit_product', methods=['GET', 'POST'])
def edit_product():
    db = get_db()
    cursor = db.cursor()
    product_id = request.args.get('product_id') if request.method == 'GET' else request.form['product_id']
    
    if request.method == 'POST':
        new_name = request.form['name']
        new_barcode = request.form['barcode']
        cursor.execute(f"UPDATE products{g.store_suffix} SET name = %s, barcode = %s WHERE id = %s", 
                      (new_name, new_barcode, product_id))
        db.commit()
        return redirect(url_for('assortment'))
    
    cursor.execute(f"SELECT id, name, barcode FROM products{g.store_suffix} WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    return render_template('edit_product.html', product=product)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/get-batches', methods=['GET'])
def get_batches():
    barcode = request.args.get('barcode')
    if not barcode:
        return jsonify({'error': 'Missing barcode'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Получаем все партии для товара
        cursor.execute(f'''
            SELECT b.expiration_date, 
                   (DATE(b.expiration_date) - CURRENT_DATE AS days_left
            FROM batches{g.store_suffix} b
            JOIN products{g.store_suffix} p ON p.id = b.product_id
            WHERE p.barcode = %s
            ORDER BY b.expiration_date ASC
        ''', (barcode,))
        
        batches = []
        today = datetime.now().date()
        
        for row in cursor.fetchall():
            exp_date = datetime.strptime(row['expiration_date'], "%Y-%m-%d").date()
            days_left = (exp_date - today).days
            
            batches.append({
                'expiration_date': exp_date.strftime('%d.%m.%Y'),
                'days_left': days_left
            })
        
        return jsonify({'batches': batches})
    
    except Exception as e:
        app.logger.error(f"Error getting batches: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = request.form['product_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM batches{g.store_suffix} WHERE product_id = %s", (product_id,))
    cursor.execute(f"DELETE FROM products{g.store_suffix} WHERE id = %s", (product_id,))
    db.commit()
    return redirect(url_for('assortment'))

def run_app():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run_app()
