import os
import psycopg2
from psycopg2.extras import DictCursor

# Подключение к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        os.environ['DATABASE_URL'],
        cursor_factory=DictCursor
    )
    return conn

# Создание таблиц для конкретного магазина
def create_store_tables(conn, store_suffix=""):
    tables = {
        'products': f'''
            CREATE TABLE IF NOT EXISTS products{store_suffix} (
                id SERIAL PRIMARY KEY,
                barcode TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL
            )
        ''',
        'batches': f'''
            CREATE TABLE IF NOT EXISTS batches{store_suffix} (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products{store_suffix}(id),
                expiration_date TEXT NOT NULL,
                added_date TEXT DEFAULT TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD')
            )
        ''',
        'history': f'''
            CREATE TABLE IF NOT EXISTS history{store_suffix} (
                id SERIAL PRIMARY KEY,
                barcode TEXT NOT NULL,
                product_name TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                removed_date TEXT NOT NULL
            )
        '''
    }
    
    with conn.cursor() as cursor:
        # Создаем таблицы
        for table_name, table_sql in tables.items():
            cursor.execute(table_sql)
        
        # Создаем уникальный индекс для batches
        cursor.execute(f'''
            CREATE UNIQUE INDEX IF NOT EXISTS unique_batch{store_suffix} 
            ON batches{store_suffix} (product_id, expiration_date)
        ''')
        
        conn.commit()

# Создаем таблицу для хранения настроек магазинов
def create_store_settings_table(conn):
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS store_settings (
                id SERIAL PRIMARY KEY,
                store_name TEXT NOT NULL UNIQUE,
                store_code TEXT NOT NULL UNIQUE,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Добавляем магазины, если их еще нет
        stores = [
            ("М1 Розыбакиева", "m1"),
            ("М2 Шевченко", "m2"),
            ("М3 Желтоксан", "m3"),
            ("М5 Сейфулина", "m5"),
            ("М6 Гоголя", "m6")
        ]
        
        for name, code in stores:
            cursor.execute('''
                INSERT INTO store_settings (store_name, store_code)
                VALUES (%s, %s)
                ON CONFLICT (store_code) DO NOTHING
            ''', (name, code))
        
        conn.commit()

# Основная функция инициализации
def init_db():
    conn = get_db_connection()
    try:
        # Создаем таблицы для каждого магазина
        create_store_settings_table(conn)
        
        # М2 Шевченко - оригинальные таблицы без суффикса
        create_store_tables(conn, "")
        
        # Остальные магазины
        for suffix in ["_m1", "_m3", "_m5", "_m6"]:
            create_store_tables(conn, suffix)
            
        print("База данных успешно инициализирована для всех магазинов")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
