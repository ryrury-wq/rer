# Обновим app.py для расчета срока годности и загрузки наименования из справочника
import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, g, jsonify
from templates import render_template

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'expiry.db')

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
        remove_date = exp_date - timedelta(days=1)
        days_left = (remove_date - today).days
        items.append((row['name'], row['barcode'], row['added_date'], row['expiration_date'], remove_date, days_left))
    return render_template('index.html', items=items, today=today.strftime('%Y-%m-%d'))

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        barcode = request.form['barcode'].strip()
        manufacture_date = request.form['manufacture_date']
        duration_value = int(request.form['duration_value'])
        duration_unit = request.form['duration_unit']

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id, name FROM products WHERE barcode = ?', (barcode,))
            product = cursor.fetchone()
            if not product:
                return render_template('scan.html', not_found=True, barcode=barcode)

            mfg_date = datetime.strptime(manufacture_date, "%Y-%m-%d")
            if duration_unit == 'days':
                expiry_date = mfg_date + timedelta(days=duration_value)
            elif duration_unit == 'months':
                expiry_date = mfg_date + timedelta(days=duration_value * 30)
            elif duration_unit == 'hours':
                expiry_date = mfg_date + timedelta(hours=duration_value)
                expiry_date = mfg_date + timedelta(days=expiry_date.hour // 24)
                expiry_date = expiry_date.replace(hour=0)

            cursor.execute('''
                INSERT INTO batches (product_id, expiration_date, added_date)
                VALUES (?, ?, ?)
            ''', (product['id'], expiry_date.strftime("%Y-%m-%d"), manufacture_date))
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
        cursor.execute("INSERT INTO batches (product_id, expiration_date) VALUES (?, ?)", (product['id'], expiration_date))
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

def remove_expired():
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT b.id, p.barcode, p.name, b.expiration_date
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE b.expiration_date < ?
    ''', (today,))
    expired = cursor.fetchall()
    
    for item in expired:
        cursor.execute("INSERT INTO history (barcode, product_name, expiration_date) VALUES (?, ?, ?)",
                       (item['barcode'], item['name'], item['expiration_date']))
        cursor.execute("DELETE FROM batches WHERE id = ?", (item['id'],))
    db.commit()


# Остальные маршруты (scan, new_product, add_batch, history) остаются без изменений
# ... [код остальных маршрутов из предыдущей версии] ...

# Импорт шаблонов
from templates import render_template

# Запуск приложения
def run():
    with app.app_context():
        init_db()
        clear_old_history()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    run()

