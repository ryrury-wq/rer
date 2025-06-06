import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, g, jsonify

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'expiry.db')

# Подключение к БД
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

# Очистка старых записей истории
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
    one_month_ago = today - timedelta(days=30)
    
    cursor.execute('''
        SELECT b.id, p.barcode, p.name, b.expiration_date
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE DATE(b.expiration_date) <= ?
    ''', (one_month_ago.strftime('%Y-%m-%d'),))
    expired = cursor.fetchall()

    for item in expired:
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
        barcode = request.form['barcode']
        name = request.form['name']
        manufacture_date = request.form['manufacture_date']
        duration_value = int(request.form['duration_value'])
        duration_unit = request.form['duration_unit']
        
        # Рассчет срока годности
        m_date = datetime.strptime(manufacture_date, '%Y-%m-%d')
        if duration_unit == 'days':
            exp_date = m_date + timedelta(days=duration_value)
        elif duration_unit == 'months':
            exp_date = m_date + timedelta(days=duration_value*30)
        elif duration_unit == 'hours':
            exp_date = m_date + timedelta(hours=duration_value)
        else:
            exp_date = m_date + timedelta(days=30)
        
        exp_date_str = exp_date.strftime('%Y-%m-%d')
        
        # Сохранение в БД
        db = get_db()
        cursor = db.cursor()
        
        # Проверка существования товара
        cursor.execute("SELECT id FROM products WHERE barcode = ?", (barcode,))
        product = cursor.fetchone()
        
        if not product:
            cursor.execute("INSERT INTO products (barcode, name) VALUES (?, ?)", (barcode, name))
            product_id = cursor.lastrowid
        else:
            product_id = product['id']
        
        cursor.execute("INSERT INTO batches (product_id, expiration_date) VALUES (?, ?)", 
                      (product_id, exp_date_str))
        db.commit()
        
        return redirect(url_for('index'))
        
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
        remove_expired()
        clear_old_history()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# Импорт шаблонов после объявления app
from templates import render_template

if __name__ == '__main__':
    run_app()
