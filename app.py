import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, g

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'expiry.db')

# Функция для подключения к БД
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Инициализация базы данных
def init_db():
    print("\n" + "="*50)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
    print(f"Создаю таблицы в файле: {DATABASE}")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Создаем таблицу продуктов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT
            )
        ''')
        
        # Создаем таблицу партий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                expiration_date DATE,
                added_date DATE DEFAULT (date('now')),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Создаем таблицу истории
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT,
                product_name TEXT,
                expiration_date DATE,
                removed_date DATE DEFAULT (date('now'))
            )
        ''')
        
        db.commit()
        print("Таблицы успешно созданы!")
        
        # Проверка создания таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Созданные таблицы:", [table['name'] for table in tables])
        
    except Exception as e:
        print("ОШИБКА при создании таблиц:", str(e))
    finally:
        cursor.close()
    
    print("="*50 + "\n")

# Очистка старых записей истории
def clear_old_history():
    try:
        db = get_db()
        cursor = db.cursor()
        one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM history WHERE removed_date < ?", (one_month_ago,))
        db.commit()
        print(f"Удалено старых записей: {cursor.rowcount}")
    except Exception as e:
        print("Ошибка очистки истории:", str(e))

# Закрываем соединение с БД при завершении
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Главная страница
@app.route('/')
def index():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Получаем товары с истекающими сроками
        cursor.execute('''
            SELECT p.barcode, p.name, b.expiration_date 
            FROM batches b
            JOIN products p ON b.product_id = p.id
            ORDER BY b.expiration_date ASC
        ''')
        items = cursor.fetchall()
        
        return render_template('index.html', items=items, today=datetime.now().strftime('%Y-%m-%d'))
    except Exception as e:
        return f"Ошибка базы данных: {str(e)}"
    
@app.route('/scan', methods=['GET', 'POST'])
def scan():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        barcode = request.form['barcode']
        cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
        product = cursor.fetchone()
        if product:
            return redirect(url_for('add_batch', barcode=barcode))
        else:
            return redirect(url_for('new_product', barcode=barcode))

    cursor.execute("SELECT name, barcode FROM products ORDER BY name ASC")
    items = cursor.fetchall()
    return render_template('scan.html', items=items)


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
if __name__ == '__main__':
    # Создаем БД при первом запуске
    if not os.path.exists(DATABASE):
        print(f"Файл базы данных не найден, создаю новый: {DATABASE}")
        open(DATABASE, 'a').close()  # Создаем пустой файл

# Инициализация в контексте приложения
    with app.app_context():
        init_db()
        clear_old_history()
    
    # Запуск сервера
    print("\nСервер запущен!")
    print(f"Доступ по адресу: http://192.168.31.109:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)