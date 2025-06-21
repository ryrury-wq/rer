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

    cursor.execute('''
        SELECT b.id, p.name, p.barcode, b.expiration_date, b.added_date
        FROM batches b
        JOIN products p ON p.id = b.product_id
        ORDER BY b.expiration_date ASC
    ''')

    items = []
    for row in cursor.fetchall():
        exp_date = datetime.strptime(row['expiration_date'], "%Y-%m-%d").date()
        days_until_expiry = (exp_date - today).days
        days_since_expiry = max(0, (today - exp_date).days)
        removal_date = exp_date + timedelta(days=30)
        days_until_removal = max(0, (removal_date - today).days)
        status = "normal"
        if days_since_expiry > 0 or days_until_expiry == 0:
            status = "expired"
        elif days_until_expiry == 1:
            status = "warning"
        elif days_until_expiry <= 7:
            status = "soon"
        items.append({
            'id': row['id'],
            'name': row['name'],
            'barcode': row['barcode'],
            'expiration_date': row['expiration_date'],
            'days_since_expiry': days_since_expiry,
            'days_until_removal': days_until_removal,
            'removal_date': removal_date.strftime('%Y-%m-%d'),
            'days_until_expiry': days_until_expiry,
            'status': status
        })
    return render_template('index.html', items=items)

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

from templates import render_template

def run_app():
    with app.app_context():
        init_db()
        remove_expired()
        clear_old_history()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run_app()
