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
<html>
<head>
    <title>Вкусвилл - Выбор магазина</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9f5e9 100%);
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px 0;
            border-bottom: 2px solid #4CAF50;
        }
        
        .logo {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 5px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #388E3C;
            margin-bottom: 20px;
        }
        
        .store-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 20px;
        }
        
        .store-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            display: flex;
            align-items: center;
        }
        
        .store-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.12);
            border-color: #4CAF50;
        }
        
        .store-icon {
            width: 50px;
            height: 50px;
            background: #E8F5E9;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            font-weight: bold;
            color: #4CAF50;
            font-size: 1.5rem;
        }
        
        .store-info {
            flex: 1;
        }
        
        .store-name {
            font-weight: bold;
            font-size: 1.2rem;
            color: #2E7D32;
            margin-bottom: 5px;
        }
        
        .store-address {
            color: #666;
            font-size: 0.95rem;
        }
        
        .store-radio {
            display: none;
        }
        
        .store-radio:checked + .store-card {
            border-color: #4CAF50;
            background-color: #F1F8E9;
            box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.3);
        }
        
        .submit-btn {
            background: linear-gradient(to bottom, #4CAF50, #388E3C);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            margin-top: 30px;
            width: 100%;
            font-weight: bold;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
            transition: all 0.3s;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
            background: linear-gradient(to bottom, #43A047, #2E7D32);
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 0.9rem;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">ВКУСВИЛЛ</div>
        <div class="subtitle">Система контроля сроков годности</div>
        <h1>Выберите ваш магазин</h1>
    </div>
    
    <form method="post" action="/select_store">
        <div class="store-container">
            <label>
                <input class="store-radio" type="radio" name="store_code" value="m1" required>
                <div class="store-card">
                    <div class="store-icon">M1</div>
                    <div class="store-info">
                        <div class="store-name">Розыбакиева</div>
                        <div class="store-address">ул. Розыбакиева, 247/1</div>
                    </div>
                </div>
            </label>
            
            <label>
                <input class="store-radio" type="radio" name="store_code" value="m2">
                <div class="store-card">
                    <div class="store-icon">M2</div>
                    <div class="store-info">
                        <div class="store-name">Шевченко</div>
                        <div class="store-address">ул. Шевченко, 124</div>
                    </div>
                </div>
            </label>
            
            <label>
                <input class="store-radio" type="radio" name="store_code" value="m3">
                <div class="store-card">
                    <div class="store-icon">M3</div>
                    <div class="store-info">
                        <div class="store-name">Желтоксан</div>
                        <div class="store-address">ул. Желтоксан, 75</div>
                    </div>
                </div>
            </label>
            
            <label>
                <input class="store-radio" type="radio" name="store_code" value="m5">
                <div class="store-card">
                    <div class="store-icon">M5</div>
                    <div class="store-info">
                        <div class="store-name">Сейфулина</div>
                        <div class="store-address">ул. Сейфулина, 483</div>
                    </div>
                </div>
            </label>
            
            <label>
                <input class="store-radio" type="radio" name="store_code" value="m6">
                <div class="store-card">
                    <div class="store-icon">M6</div>
                    <div class="store-info">
                        <div class="store-name">Гоголя</div>
                        <div class="store-address">ул. Гоголя, 58</div>
                    </div>
                </div>
            </label>
        </div>
        
        <button type="submit" class="submit-btn">Продолжить в магазин</button>
    </form>
    
    <div class="footer">
        Вкусвилл &copy; 2023 | Система контроля сроков годности
    </div>
</body>
</html>
'''

index_html = '''
<!DOCTYPE html>
<html>
<head>
    <!-- Favicon и PWA мета-теги -->
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='icon-192x192.png') }}">
    <meta name="apple-mobile-web-app-title" content="Вкусвилл">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="theme-color" content="#00a046">
    <link rel="manifest" href="{{ url_for('static', filename='manifest.json') }}">
    <title>Контроль сроков - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        body {
            font-family: 'Roboto', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            height: 60px; /* Увеличим высоту для кнопок */
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            color: white;
            margin: 0 auto; /* Центрирование по горизонтали */
            max-width: 70%; /* Защита от переполнения */
            z-index: 1;
        }
        
        /* Кнопка фильтра - исправленное позиционирование */
        .filter-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            font-size: 1.5em;
            cursor: pointer;
            padding: 8px 12px;
            border-radius: 50%;
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
        }
        
        .filter-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .container {
            max-width: 100%;
            padding: 15px;
        }

        h1 {
            font-size: 1.5em;
            margin-bottom: 10px;
            text-align: center;
            color: #00a046;
        }

        .search-container {
            position: relative;
            margin: 15px 0;
        }
        .search-input {
            width: 100%;
            padding: 12px 20px 12px 40px;
            border-radius: 24px;
            border: 1px solid #e0e0e0;
            font-size: 1em;
            box-sizing: border-box;
            background-color: white;
        }
        .search-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #757575;
        }

        .nav-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
            justify-content: center;
        }

        .nav-links a {
            padding: 12px 20px;
            background: #00a046;
            border-radius: 24px;
            text-decoration: none;
            color: white;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            min-width: calc(50% - 10px);
            box-sizing: border-box;
            text-align: center;
        }

        .items-container {
            max-height: 55vh;
            overflow-y: auto;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
            position: relative;
            padding-right: 50px;
        }

        /* Цветовые статусы для товаров */
        .item.expired { 
            background-color: #ffebee; 
            border-left: 4px solid #f44336; 
        }
        .item.warning { 
            background-color: #fff3e0; 
            border-left: 4px solid #ff9800; 
        }
        .item.soon { 
            background-color: #fff8e1; 
            border-left: 4px solid #ffc107; 
        }
        .item.normal { 
            background-color: #e8f5e9; 
            border-left: 4px solid #4caf50; 
        }

        .item-info {
            flex-grow: 1;
            max-width: calc(100% - 50px);
        }

        .item-actions {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .action-btn {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #f0f0f0;
            color: #333;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }

        .move-btn { background: #00a046; color: white; }
        .edit-btn { background: #ffc107; color: #333; }
        .delete-btn { background: #f44336; color: white; }

        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
            margin-top: 5px;
        }

        .expired-badge { background: #ffcdd2; color: #c62828; }
        .warning-badge { background: #ffe0b2; color: #e65100; }
        .soon-badge { background: #fff59d; color: #f57f17; }
        .normal-badge { background: #c8e6c9; color: #2e7d32; }

        .no-items {
            text-align: center;
            padding: 30px;
            color: #9e9e9e;
            font-style: italic;
        }

        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
            margin-top: 10px;
        }

        /* Кнопка установки - НОВЫЕ СТИЛИ */
        #install-button {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            border-radius: 24px;
            padding: 8px 15px;
            font-size: 0.9em;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 2;
            white-space: nowrap;
        }
        
        #install-button:hover {
            background: rgba(255,255,255,0.3);
        }
        
        #install-button .install-icon {
            font-size: 1.2em;
        }

        /* Модальное окно фильтров */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            display: none;
        }

        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 20px;
            width: 90%;
            max-width: 400px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            animation: modalFadeIn 0.3s ease-out;
        }

        @keyframes modalFadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }

        .modal-title {
            font-size: 1.3em;
            font-weight: 500;
            color: #00a046;
            margin: 0;
        }

        .close-modal {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #757575;
        }

        .filter-block {
            margin-bottom: 20px;
        }

        .date-filter-group {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }

        .date-input {
            flex: 1;
            min-width: 120px;
            padding: 10px 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 0.95em;
            text-align: center;
        }

        .filter-buttons {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        .filter-buttons .apply-btn,
        .filter-buttons .reset-btn {
            flex: 1;
            margin: 0;
            padding: 12px;
            font-size: 0.95em;
        }

        .quick-btns {
            margin-bottom: 0;
        }
        
        .apply-btn, .reset-btn {
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            font-size: 1em;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            display: block;
            width: 100%;
            margin-top: 10px;
        }

        .apply-btn {
            background: #00a046;
            color: white;
        }

        .reset-btn {
            background: #e0e0e0;
            color: #333;
        }

        .quick-btns {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }

        .quick-btn {
            padding: 10px 15px;
            font-size: 0.9em;
            background: #e8f5e9;
            color: #2e7d32;
            border-radius: 8px;
            text-decoration: none;
            border: 1px solid #c8e6c9;
            flex: 1;
            min-width: calc(50% - 10px);
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .quick-btn:hover {
            background: #c8e6c9;
        }

        .quick-btn.active {
            background: #00a046;
            color: white;
            border-color: #00a046;
        }
        .apply-btn:hover {
            background: #008c3a;
            transform: translateY(-2px);
        }

        .reset-btn:hover {
            background: #d0d0d0;
            transform: translateY(-2px);
        }

        @media (max-width: 480px) {
            .logo {
                font-size: 1.5em;
                max-width: 60%;
            }
            
            #install-button span:not(.install-icon) {
                display: none;
            }
            
            #install-button {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <button id="install-button" title="Установить приложение" style="display: none;">
            <span class="install-icon">⬇️</span> <span>Установить</span>
        </button>
        
        <h1 class="logo">Вкусвилл</h1>
        
        <button class="filter-btn" id="open-filter-modal">☰</button>
    </div>

    <div class="container">
        <h1>Товары с истекающим сроком</h1>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-input" placeholder="Поиск по названию или штрих-коду...">
        </div>

        <div class="nav-links">
            <a href="/scan">Сканировать</a>
            <a href="/history">История</a>
            <a href="/assortment">Ассортимент</a>
        </div>

        <div class="items-container" id="items-container">
            {% for item in items %}
                <div class="item {{ item.status }}">
                    <div class="item-info">
                        <strong>{{ item.name }}</strong>
                        <div style="font-size:0.9em; color:#666; margin-top:3px">{{ item.barcode }}</div>
                        <div>Годен до: {{ item.expiration_date }}</div>

                        {% if item.status == "expired" %}
                            <div class="badge expired-badge">Просрочено: {{ item.days_since_expiry }} дн.</div>
                        {% elif item.status == "warning" %}
                            <div class="badge warning-badge">Истекает сегодня!</div>
                        {% elif item.status == "soon" %}
                            <div class="badge soon-badge">Истекает через: {{ item.days_until_expiry }} дн.</div>
                        {% else %}
                            <div class="badge normal-badge">До истечения: {{ item.days_until_expiry }} дн.</div>
                        {% endif %}

                        <div style="font-size:0.85em; margin-top:5px; color:#757575">
                            Удаление: {{ item.removal_date }} (через {{ item.days_until_removal }} дн.)
                        </div>
                    </div>
                    <div class="item-actions">
                        <form action="/move_to_history" method="POST">
                            <input type="hidden" name="batch_id" value="{{ item.id }}">
                            <button type="submit" class="action-btn move-btn">→</button>
                        </form>
                        <a href="/edit_batch?batch_id={{ item.id }}" class="action-btn edit-btn">✎</a>
                        <form action="/delete_batch" method="POST">
                            <input type="hidden" name="batch_id" value="{{ item.id }}">
                            <button type="submit" class="action-btn delete-btn">🗑</button>
                        </form>
                    </div>
                </div>
            {% else %}
                <div class="no-items">Нет товаров с истекающим сроком</div>
            {% endfor %}
        </div>
    </div>

    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>

    <!-- Модальное окно фильтров -->
    <div class="modal-overlay" id="filter-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Фильтры</h3>
                <button class="close-modal" id="close-filter-modal">×</button>
            </div>
            
            <form id="filter-form" method="get">
                <div class="filter-block">
                    <div class="date-filter-group">
                        <input type="text" id="from_date_text" name="from_date" placeholder="От (дд.мм.гггг)" value="{{ from_date or '' }}" class="date-input">
                        <input type="text" id="to_date_text" name="to_date" placeholder="До (дд.мм.гггг)" value="{{ to_date or '' }}" class="date-input">
                    </div>
                    
                    <div class="quick-btns">
                        <a href="/?days_left=1" class="quick-btn {% if request.args.get('days_left') == '1' %}active{% endif %}">1 день</a>
                        <a href="/?days_left=2" class="quick-btn {% if request.args.get('days_left') == '2' %}active{% endif %}">1-2 дня</a>
                        <a href="/?days_left=5" class="quick-btn {% if request.args.get('days_left') == '5' %}active{% endif %}">1-5 дней</a>
                        <a href="/" class="quick-btn">Все</a>
                    </div>
                    
                    <div class="filter-buttons">
                        <button type="submit" class="apply-btn">Применить</button>
                        <a href="/" class="reset-btn">Сбросить фильтры</a>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <script>
    function setupDateInput(id) {
        const input = document.getElementById(id);
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.substr(0, 8);
            let formatted = '';
            for (let i = 0; i < value.length; i++) {
                if (i === 2 || i === 4) formatted += '.';
                formatted += value[i];
            }
            e.target.value = formatted;
        });

        input.addEventListener('keydown', function (e) {
            if ([8, 9, 13, 27, 46, 37, 39].includes(e.keyCode) ||
                (e.keyCode >= 48 && e.keyCode <= 57) ||
                (e.keyCode >= 96 && e.keyCode <= 105)) return;
            e.preventDefault();
        });
    }

    // Управление модальным окном
    document.addEventListener('DOMContentLoaded', () => {
        const modal = document.getElementById('filter-modal');
        const openBtn = document.getElementById('open-filter-modal');
        const closeBtn = document.getElementById('close-filter-modal');
        
        openBtn.addEventListener('click', () => {
            modal.style.display = 'flex';
        });
        
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Настройка полей ввода дат
        setupDateInput('from_date_text');
        setupDateInput('to_date_text');

        // Поиск по товарам
        const searchInput = document.getElementById('search-input');
        const itemsContainer = document.getElementById('items-container');
        const originalHTML = itemsContainer.innerHTML;

        searchInput.addEventListener('input', () => {
            const term = searchInput.value.toLowerCase();
            const items = itemsContainer.querySelectorAll('.item');
            let found = false;

            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(term)) {
                    item.style.display = 'flex';
                    found = true;
                } else {
                    item.style.display = 'none';
                }
            });

            if (!found && term.length > 0) {
                itemsContainer.innerHTML = `<div class="no-items">Ничего не найдено по запросу: "${term}"</div>`;
            } else if (!term) {
                itemsContainer.innerHTML = originalHTML;
            }
        });
    });
    </script>
<script>
let deferredPrompt;

// Показываем кнопку при возможности установки
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    const installButton = document.getElementById('install-button');
    if (installButton) {
        installButton.style.display = 'flex';
        
        installButton.addEventListener('click', () => {
            // Скрыть кнопку после нажатия
            installButton.style.display = 'none';
            
            // Показать подсказку установки
            deferredPrompt.prompt();
            
            // Ждем, пока пользователь решит
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('Пользователь установил приложение');
                } else {
                    console.log('Пользователь отказался от установки');
                }
                deferredPrompt = null;
            });
        });
    }
});

// Скрываем кнопку после установки
window.addEventListener('appinstalled', () => {
    console.log('Приложение успешно установлено');
    const installButton = document.getElementById('install-button');
    if (installButton) {
        installButton.style.display = 'none';
    }
});
</script>
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
