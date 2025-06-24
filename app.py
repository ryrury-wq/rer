import os
import psycopg2
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, g, jsonify
from psycopg2.extras import DictCursor
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

# Подключение к PostgreSQL
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

# Инициализация БД
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                barcode TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batches (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id),
                expiration_date TEXT NOT NULL,
                added_date TEXT DEFAULT TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD')
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                type TEXT NOT NULL,  -- 'today' или 'soon'
                product_id INTEGER REFERENCES products(id),
                batch_id INTEGER REFERENCES batches(id),
                notification_date TEXT DEFAULT TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD'),
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                barcode TEXT NOT NULL,
                product_name TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                removed_date TEXT NOT NULL
            )
        ''')
        db.commit()

def clear_old_history():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM history WHERE removed_date < %s", (three_months_ago,))
        db.commit()

def generate_notifications():
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date()
    
    # Проверяем, не заглушены ли уведомления
    cursor.execute("SELECT notification_date FROM notifications WHERE type LIKE 'mute_%'")
    mute_notification = cursor.fetchone()
    
    if mute_notification:
        mute_date = datetime.strptime(mute_notification['notification_date'], '%Y-%m-%d').date()
        if mute_date > today:
            # Уведомления заглушены, пропускаем генерацию
            return
    
    # Удаляем старые уведомления (старше 6 дней)
    six_days_ago = (today - timedelta(days=6)).strftime('%Y-%m-%d')
    cursor.execute("DELETE FROM notifications WHERE notification_date < %s", (six_days_ago,))
    
    # Удаляем старые уведомления о заглушении
    cursor.execute("DELETE FROM notifications WHERE type LIKE 'mute_%' AND notification_date < %s", (today.strftime('%Y-%m-%d'),))
    
    # Генерируем уведомления для товаров, которые нужно убрать сегодня
    cursor.execute('''
        INSERT INTO notifications (type, product_id, batch_id, notification_date)
        SELECT 'today', p.id, b.id, %s
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE b.expiration_date = %s
        AND NOT EXISTS (
            SELECT 1 FROM notifications n 
            WHERE n.batch_id = b.id 
            AND n.type = 'today'
            AND n.notification_date = %s
        )
    ''', (today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')))
    
    # Генерируем уведомления для товаров с истекающим сроком (2-5 дней)
    soon_start = today + timedelta(days=2)
    soon_end = today + timedelta(days=5)
    
    cursor.execute('''
        INSERT INTO notifications (type, product_id, batch_id, notification_date)
        SELECT 'soon', p.id, b.id, %s
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE b.expiration_date BETWEEN %s AND %s
        AND NOT EXISTS (
            SELECT 1 FROM notifications n 
            WHERE n.batch_id = b.id 
            AND n.type = 'soon'
            AND n.notification_date = %s
        )
    ''', (today.strftime('%Y-%m-%d'), 
          soon_start.strftime('%Y-%m-%d'), 
          soon_end.strftime('%Y-%m-%d'),
          today.strftime('%Y-%m-%d')))
    
    # Удаляем уведомления для товаров, которые больше не соответствуют условиям
    # Для today: удаляем если срок больше не сегодня
    cursor.execute('''
        DELETE FROM notifications n
        USING batches b
        WHERE n.batch_id = b.id
        AND n.type = 'today'
        AND b.expiration_date != %s
    ''', (today.strftime('%Y-%m-%d'),))
    
    # Для soon: удаляем если срок больше не в диапазоне 2-5 дней
    cursor.execute('''
        DELETE FROM notifications n
        USING batches b
        WHERE n.batch_id = b.id
        AND n.type = 'soon'
        AND b.expiration_date NOT BETWEEN %s AND %s
    ''', (soon_start.strftime('%Y-%m-%d'), soon_end.strftime('%Y-%m-%d')))
    
    db.commit()

def remove_expired():
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)

    cursor.execute('''
        SELECT b.id, p.barcode, p.name, b.expiration_date
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE b.expiration_date <= %s
    ''', (one_month_ago.strftime('%Y-%m-%d'),))
    expired = cursor.fetchall()

    for item in expired:
        cursor.execute("SELECT id FROM history WHERE barcode = %s AND expiration_date = %s",
                       (item['barcode'], item['expiration_date']))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO history (barcode, product_name, expiration_date, removed_date) 
                VALUES (%s, %s, %s, %s)
            """, (item['barcode'], item['name'], item['expiration_date'], today.strftime('%Y-%m-%d')))
        cursor.execute("DELETE FROM batches WHERE id = %s", (item['id'],))
    db.commit()

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

    query = '''
        SELECT b.id, p.name, p.barcode, b.expiration_date, b.added_date
        FROM batches b
        JOIN products p ON p.id = b.product_id
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

        if days_since_expiry > 1:
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
        try:
            barcode = request.form['barcode']
            name = request.form['name']
            manufacture_date = request.form['manufacture_date']
            duration_value = int(request.form['duration_value'])
            duration_unit = request.form['duration_unit']

            m_date = datetime.strptime(manufacture_date, '%Y-%m-%d').date()
            
            # Используем точный расчет с relativedelta
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

            db = get_db()
            cursor = db.cursor()

            cursor.execute("SELECT id FROM products WHERE barcode = %s", (barcode,))
            product = cursor.fetchone()

            if not product:
                cursor.execute("INSERT INTO products (barcode, name) VALUES (%s, %s) RETURNING id", (barcode, name))
                product_id = cursor.fetchone()['id']
            else:
                product_id = product['id']

            cursor.execute("INSERT INTO batches (product_id, expiration_date) VALUES (%s, %s)",
                           (product_id, exp_date_str))
            db.commit()

            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"Scan POST Error: {str(e)}")
            return f"Server Error: {str(e)}", 500
    return render_template('scan.html')

@app.route('/get-product-name', methods=['GET'])
def get_product_name():
    barcode = request.args.get('barcode')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name FROM products WHERE barcode = %s', (barcode,))
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
    
    if not barcode:
        return redirect(url_for('assortment'))

    cursor.execute("SELECT id, name FROM products WHERE barcode = %s", (barcode,))
    product = cursor.fetchone()

    if not product:
        return redirect(url_for('assortment'))

    if request.method == 'POST':
        manufacture_date = request.form.get('manufacture_date')
        duration_value = request.form.get('duration_value')
        duration_unit = request.form.get('duration_unit')
        expiration_date = request.form.get('expiration_date')
        
        # Если указана дата изготовления и срок
        if manufacture_date and duration_value and duration_unit:
            m_date = datetime.strptime(manufacture_date, '%Y-%m-%d').date()
            
            if duration_unit == 'days':
                exp_date = m_date + timedelta(days=int(duration_value))
            elif duration_unit == 'months':
                exp_date = m_date + relativedelta(months=int(duration_value))
            elif duration_unit == 'years':
                exp_date = m_date + relativedelta(years=int(duration_value))
            else:
                exp_date = m_date + timedelta(days=30)
                
            expiration_date = exp_date.strftime('%Y-%m-%d')
        
        # Если указана конкретная дата истечения
        elif expiration_date:
            expiration_date = expiration_date
        else:
            return "Не указаны данные о сроке годности", 400

        cursor.execute("""
            INSERT INTO batches (product_id, expiration_date) 
            VALUES (%s, %s)
        """, (product['id'], expiration_date))
        db.commit()
        return redirect(url_for('assortment'))

    return render_template('add_batch.html', 
                           product_name=product['name'],
                           barcode=barcode)

@app.route('/assortment')
def assortment():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT p.id, p.barcode, p.name, 
               (SELECT COUNT(*) FROM batches b WHERE b.product_id = p.id) AS batch_count
        FROM products p
        ORDER BY p.name
    ''')
    products = cursor.fetchall()
    return render_template('assortment.html', products=products)

@app.route('/history')
def history():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM history ORDER BY removed_date DESC")
    history_items = cursor.fetchall()
    return render_template('history.html', history_items=history_items)

@app.route('/move_to_history', methods=['POST'])
def move_to_history():
    batch_id = int(request.form['batch_id'])  # Явное преобразование в int
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date().strftime('%Y-%m-%d')
    
    # Получаем информацию о товаре
    cursor.execute('''
    SELECT p.barcode, p.name, b.expiration_date
    FROM batches b
    JOIN products p ON b.product_id = p.id
    WHERE b.id = %s
''', (batch_id,)) 
    item = cursor.fetchone()
    
    if item:
        # Проверяем, нет ли уже такой записи в истории
        cursor.execute("SELECT id FROM history WHERE barcode = %s AND expiration_date = %s",
                     (item['barcode'], item['expiration_date']))
        if not cursor.fetchone():
            # Добавляем в историю
            cursor.execute("INSERT INTO history (barcode, product_name, expiration_date, removed_date) VALUES (%s, %s, %s, %s)",
                          (item['barcode'], item['name'], item['expiration_date'], today))
        
        # Удаляем из активных
        cursor.execute("DELETE FROM batches WHERE id = %s", (batch_id,))
        db.commit()
    
    return redirect(url_for('index'))

@app.route('/restore_from_history', methods=['POST'])
def restore_from_history():
    history_id = request.form['history_id']
    db = get_db()
    cursor = db.cursor()
    
    # Получаем информацию из истории
    cursor.execute("SELECT * FROM history WHERE id = %s", (history_id,))
    item = cursor.fetchone()
    
    if item:
        # Проверяем существование товара
        cursor.execute("SELECT id FROM products WHERE barcode = %s", (item['barcode'],))
        product = cursor.fetchone()
        
        if not product:
            # Если товара нет, создаем новый
            cursor.execute("INSERT INTO products (barcode, name) VALUES (%s, %s)", 
                          (item['barcode'], item['product_name']))
            product_id = cursor.lastrowid
        else:
            product_id = product['id']
        
        # Добавляем обратно в активные
        cursor.execute("INSERT INTO batches (product_id, expiration_date) VALUES (%s, %s)", 
                      (product_id, item['expiration_date']))
        
        # Удаляем из истории
        cursor.execute("DELETE FROM history WHERE id = %s", (history_id,))
        db.commit()
    
    return redirect(url_for('history'))

@app.route('/edit_batch', methods=['GET', 'POST'])
def edit_batch():
    batch_id = request.args.get('batch_id') if request.method == 'GET' else request.form['batch_id']
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        new_date = request.form['expiration_date']
        cursor.execute("UPDATE batches SET expiration_date = %s WHERE id = %s", (new_date, batch_id))
        db.commit()
        return redirect(url_for('index'))
    
    cursor.execute("""
        SELECT b.id, b.expiration_date, p.name, p.barcode 
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE b.id = %s
    """, (batch_id,))
    batch = cursor.fetchone()
    
    return render_template('edit_batch.html', batch=batch)

@app.route('/delete_batch', methods=['POST'])
def delete_batch():
    batch_id = request.form['batch_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM batches WHERE id = %s", (batch_id,))
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
        cursor.execute("UPDATE products SET name = %s, barcode = %s WHERE id = %s", 
                      (new_name, new_barcode, product_id))
        db.commit()
        return redirect(url_for('assortment'))
    
    cursor.execute("SELECT id, name, barcode FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    return render_template('edit_product.html', product=product)

@app.route('/notifications')
def notifications():
    db = get_db()
    cursor = db.cursor()
    
    # Получаем все активные уведомления
    cursor.execute('''
        SELECT n.id, n.type, n.notification_date, 
               p.name, p.barcode, b.expiration_date
        FROM notifications n
        JOIN products p ON n.product_id = p.id
        JOIN batches b ON n.batch_id = b.id
        WHERE n.is_active = TRUE
        ORDER BY n.notification_date DESC, n.type
    ''')
    notifications = cursor.fetchall()
    
    # Группируем по дате и типу
    grouped = {}
    for note in notifications:
        date = note['notification_date']
        if date not in grouped:
            grouped[date] = {'today': [], 'soon': []}
        
        item = {
            'id': note['id'],
            'name': note['name'],
            'barcode': note['barcode'],
            'expiration_date': datetime.strptime(note['expiration_date'], '%Y-%m-%d').strftime('%d.%m.%Y')
        }
        
        grouped[date][note['type']].append(item)
    
    return render_template('notifications.html', notifications=grouped)

@app.route('/mute_notifications', methods=['POST'])
def mute_notifications():
    mute_type = request.form['mute_type']
    db = get_db()
    cursor = db.cursor()
    
    if mute_type == 'weekend':
        # Заглушить на 2 дня (выходные)
        mute_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    else:  # vacation
        # Заглушить до отпуска (по умолчанию 14 дней)
        mute_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Помечаем все уведомления как неактивные
    cursor.execute("UPDATE notifications SET is_active = FALSE")
    # Создаем запись о заглушении
    cursor.execute("INSERT INTO notifications (type, notification_date) VALUES (%s, %s)", 
                  (f'mute_{mute_type}', mute_date))
    
    db.commit()
    return redirect(url_for('notifications'))

@app.route('/clear_notifications', methods=['POST'])
def clear_notifications():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM notifications")
    db.commit()
    return redirect(url_for('notifications'))

@app.route('/check_new_notifications')
def check_new_notifications():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_active = TRUE")
    count = cursor.fetchone()[0]
    return jsonify({'count': count})

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = request.form['product_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM batches WHERE product_id = %s", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    db.commit()
    return redirect(url_for('assortment'))

from templates import render_template

def run_app():
    with app.app_context():
        init_db()
        remove_expired()
        clear_old_history()
        generate_notifications()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run_app()
