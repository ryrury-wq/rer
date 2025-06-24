from flask import render_template_string

# Главная страница с новым стилем Вкусвилл
index_html = '''
<!DOCTYPE html>
<html>
<head>
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
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            color: white;
            position: absolute; /* Абсолютное позиционирование */
            left: 50%; /* Центрируем по горизонтали */
            transform: translateX(-50%); /* Точное центрирование */
            margin: 0;
            z-index: 1;
        }
        .filter-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5em;
            cursor: pointer;
            padding: 5px 10px;
            position: absolute; /* Абсолютное позиционирование */
            right: 15px; /* Фиксируем справа */
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
            /* Убираем нижний отступ, так как кнопки теперь в отдельном контейнере */
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
    </style>
</head>
<body>
    <div class="header">
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
</body>
</html>
'''

# Стиль для страницы сканирования
scan_html = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Сканирование - Вкусвилл</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .container {
            flex: 1;
            padding: 20px 15px;
            max-width: 500px;
            margin: 0 auto;
            width: 100%;
            box-sizing: border-box;
        }
        h1 {
            text-align: center;
            color: #00a046;
            font-weight: 500;
            margin-top: 0;
        }
        .scanner-container { 
            position: relative; 
            width: 100%;
            height: 250px;
            margin: 0 auto 20px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            background: black;
        }
        video { 
            width: 100%; 
            height: 100%; 
            object-fit: cover;
        }
        .overlay { 
            position: absolute; 
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80%; 
            height: 50%;
            border: 3px solid rgba(0, 160, 70, 0.7); 
            border-radius: 12px; 
            pointer-events: none; 
            box-sizing: border-box;
        }
        .camera-error {
            color: #f44336;
            text-align: center;
            padding: 15px;
            background: #ffebee;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .camera-controls {
            margin-top: 15px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .camera-btn {
            padding: 12px 20px;
            background: #00a046;
            border-radius: 24px;
            border: none;
            cursor: pointer;
            color: white;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s;
            min-width: 150px;
        }
        .camera-btn:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .form-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-top: 20px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500;
            color: #424242;
        }
        input, select, button {
            width: 100%;
            box-sizing: border-box;
            padding: 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: 'Roboto', sans-serif;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00a046;
            box-shadow: 0 0 0 2px rgba(0, 160, 70, 0.2);
        }
        button[type="submit"] {
            background: #00a046;
            color: white;
            border: none;
            font-weight: 500;
            font-size: 1.1em;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button[type="submit"]:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .manual-input {
            margin: 20px 0;
            text-align: center;
        }
        .manual-input a {
            color: #00a046;
            text-decoration: none;
            font-weight: 500;
            border-bottom: 1px dashed #00a046;
            padding-bottom: 2px;
        }
         .date-input-group {
            position: relative;
        }
        .date-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #757575;
            pointer-events: none;
            font-size: 1.2em;
            z-index: 2; /* Убедимся, что иконка поверх других элементов */
        }
        .date-input {
            padding-left: 45px !important; /* Увеличим отступ слева */
            width: calc(100% - 45px) !important; /* Учтем отступ в ширине */
            box-sizing: border-box;
        }
        
        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
        }
        .duration-group {
            display: flex;
            gap: 10px;
        }
        .duration-group input {
            flex: 2;
        }
        .duration-group select {
            flex: 1;
        }
        .expiration-box {
            background: #f5f5f5;
            padding: 12px 15px;
            border-radius: 8px;
            font-size: 0.95em;
            border-bottom: 1px solid #e0e0e0;
        }
        .expiration-box.normal {
            background: #e8f5e9;
            border-left: 4px solid #00a046;
        }
        .expiration-box.warning {
            background: #fff8e1;
            border-left: 4px solid #ff9800;
        }
        .expiration-box.expired {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }
        .expiration-date {
            font-weight: 500;
            display: block;
            margin-bottom: 5px;
            word-break: break-word;
        }
        .days-count {
            font-size: 0.9em;
            display: block;
            word-break: break-word;
        }
        .normal-date { color: #00a046; }
        .warning-date { color: #ff9800; }
        .expired-date { color: #f44336; }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="back-btn">←</a>
        <h1 class="logo">Вкусвилл</h1>
    </div>

    <style>
        .back-btn {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 24px;
            text-decoration: none;
            font-weight: bold;
            z-index: 10;
        }
    
        .header {
            position: relative;
        }
    </style>
    
    <div class="container">
        <h1>Сканирование товара</h1>

        <div class="scanner-container">
            <video id="video" autoplay playsinline muted></video>
            <div class="overlay"></div>
            <div id="camera-error" class="camera-error" style="display: none;">
                Ошибка доступа к камере. Проверьте разрешения.
            </div>
        </div>

        <div class="camera-controls">
            <button id="restart-btn" class="camera-btn">Перезапустить</button>
            <button id="torch-btn" class="camera-btn">Фонарик</button>
        </div>

        <div class="manual-input">
            <a href="#" id="manual-input-link">Ввести штрих-код вручную</a>
        </div>

        <audio id="beep" class="beep" preload="auto"></audio>

        <div class="form-container">
            <form method="POST" id="scanner-form">
                <div class="form-group">
                    <label for="barcode">Штрих-код:</label>
                    <input type="text" name="barcode" id="barcode" placeholder="Отсканируйте или введите вручную" required>
                </div>

                <div class="form-group">
                    <label for="name">Наименование:</label>
                    <input type="text" id="name" name="name" required>
                </div>

                <div class="form-group">
                    <label for="manufacture_date_text">Дата изготовления (дд.мм.гггг):</label>
                    <div class="date-input-group">
                        <span class="date-icon">📅</span>
                        <input type="hidden" name="manufacture_date" id="manufacture_date">
                        <input type="text" id="manufacture_date_text" placeholder="дд.мм.гггг" required class="date-input">
                    </div>
                </div>

                <div class="form-group">
                    <label>Срок годности:</label>
                    <div class="duration-group">
                        <input type="number" name="duration_value" placeholder="Количество" required>
                        <select name="duration_unit">
                            <option value="days">дней</option>
                            <option value="months">месяцев</option>
                            <option value="years">лет</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <div class="expiration-box" id="expiration-box" style="display: none;">
                        <span class="expiration-date" id="expiration-date-display"></span>
                        <span class="days-count" id="days-count"></span>
                    </div>
                </div>
                <button type="submit">Сохранить товар</button>
            </form>
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>

    <script type="module">
        import { BrowserMultiFormatReader } from 'https://cdn.jsdelivr.net/npm/@zxing/browser@0.0.10/+esm';

        const codeReader = new BrowserMultiFormatReader();
        const video = document.getElementById('video');
        const barcodeInput = document.getElementById('barcode');
        const cameraError = document.getElementById('camera-error');
        const restartBtn = document.getElementById('restart-btn');
        const torchBtn = document.getElementById('torch-btn');
        const beepSound = document.getElementById('beep');
        const manualInputLink = document.getElementById('manual-input-link');
        const scannerForm = document.getElementById('scanner-form');
        
        let currentStream = null;
        let scannerActive = true;
        let torchOn = false;
        let lastScanTime = 0;
        const SCAN_COOLDOWN = 2000;
        
        function stopCurrentStream() {
            if (currentStream) {
                currentStream.getTracks().forEach(track => {
                    if (track.kind === 'video' && torchOn) {
                        track.applyConstraints({ advanced: [{ torch: false }] });
                    }
                    track.stop();
                });
                currentStream = null;
                torchOn = false;
                torchBtn.textContent = 'Фонарик';
            }
        }
        
        async function startCamera() {
            try {
                stopCurrentStream();
                
                const constraints = {
                    video: {
                        facingMode: 'environment',
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        focusMode: 'continuous'
                    }
                };
                
                currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = currentStream;
                
                cameraError.style.display = 'none';
                video.style.display = 'block';
                
                checkTorchSupport();
                startScanner();
            } catch (err) {
                console.error("Ошибка доступа к камере:", err);
                showCameraError();
            }
        }
        
        function checkTorchSupport() {
            torchBtn.style.display = 'none';
            if (currentStream) {
                const track = currentStream.getVideoTracks()[0];
                if (track && track.getCapabilities().torch) {
                    torchBtn.style.display = 'block';
                }
            }
        }
        
        async function toggleTorch() {
            if (!currentStream) return;
            
            const track = currentStream.getVideoTracks()[0];
            if (!track || !track.getCapabilities().torch) return;
            
            try {
                await track.applyConstraints({
                    advanced: [{ torch: !torchOn }]
                });
                torchOn = !torchOn;
                torchBtn.textContent = torchOn ? 'Выкл. фонарик' : 'Фонарик';
            } catch (err) {
                console.error("Ошибка переключения фонарика:", err);
            }
        }
        
        function startScanner() {
            if (!scannerActive) return;
            
            codeReader.decodeFromVideoElement(video, (result, err) => {
                if (!scannerActive) return;
                
                const now = Date.now();
                if (now - lastScanTime < SCAN_COOLDOWN) return;
                
                if (result) {
                    lastScanTime = now;
                    
                    if (beepSound) {
                        beepSound.currentTime = 0;
                        beepSound.play().catch(e => console.log("Не удалось воспроизвести звук:", e));
                    }
                    
                    barcodeInput.value = result.text;
                    document.getElementById('name').focus();
                    
                    fetch(`/get-product-name?barcode=${result.text}`)
                        .then(res => res.json())
                        .then(data => {
                            if (data.found) {
                                document.getElementById('name').value = data.name;
                            }
                        });
                }
            });
        }
        
        function stopScanner() {
            scannerActive = false;
            codeReader.reset();
        }
        
        function showCameraError() {
            cameraError.style.display = 'block';
            video.style.display = 'none';
            barcodeInput.removeAttribute('readonly');
            barcodeInput.placeholder = "Введите штрих-код вручную";
        }
        
        restartBtn.addEventListener('click', () => {
            startCamera();
        });
        
        torchBtn.addEventListener('click', toggleTorch);
        
        manualInputLink.addEventListener('click', (e) => {
            e.preventDefault();
            barcodeInput.removeAttribute('readonly');
            barcodeInput.focus();
            barcodeInput.placeholder = "Введите штрих-код вручную";
        });
        
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopScanner();
            } else {
                scannerActive = true;
                startScanner();
            }
        });
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showCameraError();
            cameraError.textContent = "Ваш браузер не поддерживает доступ к камере";
        } else {
            startCamera();
        }
        
        scannerForm.addEventListener('submit', (e) => {
            if (!barcodeInput.value) {
                e.preventDefault();
                alert("Пожалуйста, введите или отсканируйте штрих-код");
                barcodeInput.focus();
            }
        });
    </script>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const dateField = document.getElementById('manufacture_date');
        const textField = document.getElementById('manufacture_date_text');
        
        textField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.substr(0, 8);
            
            let formatted = '';
            for (let i = 0; i < value.length; i++) {
                if (i === 2 || i === 4) formatted += '.';
                formatted += value[i];
            }
            e.target.value = formatted;
            
            if (formatted.length === 10) {
                const parts = formatted.split('.');
                if (parts.length === 3) {
                    const [day, month, year] = parts;
                    dateField.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                    calculateExpirationDate(); // обновить табличку
                }
            }
        });
            
        textField.addEventListener('blur', function() {
            const value = textField.value;
            if (value.length > 0 && value.length < 10) {
                alert('Пожалуйста, введите полную дату в формате дд.мм.гггг');
                textField.focus();
            } else if (value.length === 10) {
                const parts = value.split('.');
                if (parts.length === 3) {
                    const [day, month, year] = parts;
                    dateField.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                }
            }
        });
            
        textField.addEventListener('keydown', function(e) {
            if ([46, 8, 9, 27, 13].includes(e.keyCode) || 
                (e.keyCode === 65 && e.ctrlKey === true) || 
                (e.keyCode === 67 && e.ctrlKey === true) || 
                (e.keyCode === 86 && e.ctrlKey === true) || 
                (e.keyCode === 88 && e.ctrlKey === true) || 
                (e.keyCode >= 35 && e.keyCode <= 39)) {
                return;
            }
            
            if ((e.keyCode < 48 || e.keyCode > 57) && (e.keyCode < 96 || e.keyCode > 105)) {
                e.preventDefault();
            }
        });
            
        scannerForm.addEventListener('submit', function(e) {
            if (!dateField.value) {
                e.preventDefault();
                alert('Пожалуйста, введите корректную дату изготовления в формате дд.мм.гггг');
                textField.focus();
            }
        });
    });
    </script>
    <script>
function calculateExpirationDate() {
    const dateStr = document.getElementById('manufacture_date').value;
    const durationValue = parseInt(document.querySelector('input[name="duration_value"]').value);
    const durationUnit = document.querySelector('select[name="duration_unit"]').value;

    const box = document.getElementById('expiration-box');
    const dateEl = document.getElementById('expiration-date-display');
    const daysEl = document.getElementById('days-count');

    if (!dateStr || !durationValue || durationValue <= 0) {
        box.style.display = 'none';
        return;
    }

    const [year, month, day] = dateStr.split('-');
    let mDate = new Date(year, month - 1, day);
    let expDate = new Date(mDate);

    if (durationUnit === 'days') {
        expDate.setDate(expDate.getDate() + durationValue);
    } else if (durationUnit === 'months') {
        expDate.setMonth(expDate.getMonth() + durationValue);
    } else if (durationUnit === 'years') {
        expDate.setFullYear(expDate.getFullYear() + durationValue);
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffDays = Math.ceil((expDate - today) / (1000 * 60 * 60 * 24));

    const formatted = `Годен до: ${expDate.toLocaleDateString('ru-RU')}`;
    dateEl.textContent = formatted;

    if (diffDays < 1) {
        box.className = 'expiration-box expired';
        dateEl.className = 'expiration-date expired-date';
        daysEl.textContent = `Просрочено ${Math.abs(diffDays)} дн.`;
        daysEl.className = 'days-count expired-date';
    } else if (diffDays <= 10) {
        box.className = 'expiration-box warning';
        dateEl.className = 'expiration-date warning-date';
        daysEl.textContent = `Осталось ${diffDays} дн.`;
        daysEl.className = 'days-count warning-date';
    } else {
        box.className = 'expiration-box normal';
        dateEl.className = 'expiration-date normal-date';
        daysEl.textContent = `Осталось ${diffDays} дн.`;
        daysEl.className = 'days-count normal-date';
    }

    box.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('manufacture_date').addEventListener('change', calculateExpirationDate);
    document.querySelector('input[name="duration_value"]').addEventListener('input', calculateExpirationDate);
    document.querySelector('select[name="duration_unit"]').addEventListener('change', calculateExpirationDate);
});
    </script>
</body>
</html>
'''

# Стиль для новых страниц
new_product_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Новый товар - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            min-height: 100vh;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .container {
            max-width: 500px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .form-container {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        h1 {
            text-align: center;
            color: #00a046;
            font-weight: 500;
            margin-top: 0;
            margin-bottom: 25px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500;
            color: #424242;
        }
        input, button {
            width: 100%;
            box-sizing: border-box;
            padding: 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: 'Roboto', sans-serif;
        }
        input:focus {
            outline: none;
            border-color: #00a046;
            box-shadow: 0 0 0 2px rgba(0, 160, 70, 0.2);
        }
        button { 
            background: #00a046;
            color: white;
            border: none;
            font-weight: 500;
            font-size: 1.1em;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .footer {
            text-align: center;
            padding: 30px 15px 10px;
            color: #757575;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h1>Добавление нового товара</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Штрих-код:</label>
                    <input type="text" name="barcode" value="{{ barcode }}" readonly>
                </div>
                <div class="form-group">
                    <label>Название товара:</label>
                    <input type="text" name="name" placeholder="Введите название" required>
                </div>
                <button type="submit">Сохранить</button>
            </form>
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>
</body>
</html>
'''


add_batch_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Добавить срок - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            min-height: 100vh;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
            position: relative;
        }
        .back-btn {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 24px;
            text-decoration: none;
            font-weight: bold;
            z-index: 10;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .container {
            max-width: 500px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .form-container {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        h1 {
            text-align: center;
            color: #00a046;
            font-weight: 500;
            margin-top: 0;
            margin-bottom: 25px;
        }
        .product-name {
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 10px;
            font-weight: 500;
        }
        .product-barcode {
            text-align: center;
            color: #757575;
            margin-bottom: 20px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500;
            color: #424242;
        }
        input, select {
            width: 100%;
            box-sizing: border-box;
            padding: 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: 'Roboto', sans-serif;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00a046;
            box-shadow: 0 0 0 2px rgba(0, 160, 70, 0.2);
        }
        .button-container {
            margin-top: 20px;
        }
        button { 
            width: 100%;
            background: #00a046;
            color: white;
            border: none;
            font-weight: 500;
            font-size: 1.1em;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .duration-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .duration-group input {
            flex: 1;
        }
        .duration-group select {
            flex: 1;
        }
        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
        }
        .date-input-group {
            position: relative;
        }
        .date-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #757575;
            pointer-events: none;
            font-size: 1.2em;
        }
        .date-input {
            padding-left: 40px;
        }
        .error-message {
            color: #f44336;
            font-size: 0.85em;
            margin-top: 5px;
            display: none;
        }
        .expiration-box {
            background: #f5f5f5;
            padding: 12px 15px;
            border-radius: 8px 8px 0 0;
            font-size: 0.95em;
            border-bottom: 1px solid #e0e0e0;
        }
        .expiration-box.normal {
            background: #e8f5e9;
            border-left: 4px solid #00a046;
        }
        .expiration-box.warning {
            background: #fff8e1;
            border-left: 4px solid #ff9800;
        }
        .expiration-box.expired {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }
        .expiration-date {
            font-weight: 500;
            display: block;
            margin-bottom: 5px;
            word-break: break-word;
        }
        .days-count {
            font-size: 0.9em;
            display: block;
            word-break: break-word;
        }
        .normal-date {
            color: #00a046;
        }
        .warning-date {
            color: #ff9800;
        }
        .expired-date {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/assortment" class="back-btn">←</a>
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h1>Добавление срока годности</h1>
            <div class="product-name">{{ product_name }}</div>
            <div class="product-barcode">Штрих-код: {{ barcode }}</div>
            
            <form method="POST" id="add-batch-form">
                <div class="form-group">
                    <label>Дата изготовления (дд.мм.гггг):</label>
                    <div class="date-input-group">
                        <span class="date-icon">📅</span>
                        <input type="hidden" id="manufacture_date" name="manufacture_date">
                        <input type="text" id="manufacture_date_text" class="date-input" placeholder="дд.мм.гггг" required>
                        <div class="error-message" id="manufacture_date_error">Пожалуйста, введите дату в формате дд.мм.гггг</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Срок годности:</label>
                    <div class="duration-group">
                        <input type="number" name="duration_value" id="duration_value" placeholder="Количество" required min="1">
                        <select name="duration_unit" id="duration_unit" required>
                            <option value="days">дней</option>
                            <option value="months">месяцев</option>
                            <option value="years">лет</option>
                        </select>
                    </div>
                </div>
                
                <div class="button-container">
                    <div class="expiration-box" id="expiration-box" style="display: none;">
                        <span class="expiration-date" id="expiration-date-display"></span>
                        <span class="days-count" id="days-count"></span>
                    </div>
                    <button type="submit">Добавить срок</button>
                </div>
            </form>
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Функция для обработки ввода даты
            function setupDateInput(inputId, hiddenId, errorId) {
                const textField = document.getElementById(inputId);
                const hiddenField = document.getElementById(hiddenId);
                const errorField = document.getElementById(errorId);
                
                textField.addEventListener('input', function(e) {
                    let value = e.target.value.replace(/\D/g, '');
                    if (value.length > 8) value = value.substr(0, 8);
                    
                    let formatted = '';
                    for (let i = 0; i < value.length; i++) {
                        if (i === 2 || i === 4) formatted += '.';
                        formatted += value[i];
                    }
                    e.target.value = formatted;
                    
                    if (formatted.length === 10) {
                        const parts = formatted.split('.');
                        if (parts.length === 3) {
                            const [day, month, year] = parts;
                            hiddenField.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                            errorField.style.display = 'none';
                            calculateExpirationDate();
                        }
                    }
                });
                
                textField.addEventListener('blur', function() {
                    const value = textField.value;
                    if (value.length > 0 && value.length < 10) {
                        errorField.style.display = 'block';
                    } else if (value.length === 10) {
                        const parts = value.split('.');
                        if (parts.length === 3) {
                            const [day, month, year] = parts;
                            hiddenField.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                            errorField.style.display = 'none';
                            calculateExpirationDate();
                        } else {
                            errorField.style.display = 'block';
                        }
                    }
                });
                
                textField.addEventListener('keydown', function(e) {
                    if ([46, 8, 9, 27, 13].includes(e.keyCode) || 
                        (e.keyCode === 65 && e.ctrlKey === true) || 
                        (e.keyCode === 67 && e.ctrlKey === true) || 
                        (e.keyCode === 86 && e.ctrlKey === true) || 
                        (e.keyCode === 88 && e.ctrlKey === true) || 
                        (e.keyCode >= 35 && e.keyCode <= 39)) {
                        return;
                    }
                    
                    if ((e.keyCode < 48 || e.keyCode > 57) && (e.keyCode < 96 || e.keyCode > 105)) {
                        e.preventDefault();
                    }
                });
            }
            
            // Функция для расчета даты истечения срока
            function calculateExpirationDate() {
                const manufactureDate = document.getElementById('manufacture_date').value;
                const durationValue = document.getElementById('duration_value').value;
                const durationUnit = document.getElementById('duration_unit').value;
                
                if (manufactureDate && durationValue) {
                    const [year, month, day] = manufactureDate.split('-');
                    const mDate = new Date(year, month - 1, day);
                    
                    let expDate = new Date(mDate);
                    const duration = parseInt(durationValue);
                    
                    if (durationUnit === 'days') {
                        expDate.setDate(mDate.getDate() + duration);
                    } else if (durationUnit === 'months') {
                        expDate.setMonth(mDate.getMonth() + duration);
                    } else if (durationUnit === 'years') {
                        expDate.setFullYear(mDate.getFullYear() + duration);
                    }
                    
                    // Форматируем дату для отображения
                    const formattedDate = `Годен до: ${expDate.getDate().toString().padStart(2, '0')}.${(expDate.getMonth() + 1).toString().padStart(2, '0')}.${expDate.getFullYear()}`;
                    
                    // Рассчитываем оставшиеся дни
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const diffTime = expDate - today;
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    
                    // Устанавливаем стиль в зависимости от срока
                    const expirationBox = document.getElementById('expiration-box');
                    const dateDisplay = document.getElementById('expiration-date-display');
                    const daysCount = document.getElementById('days-count');
                    
                    expirationBox.style.display = 'block';
                    dateDisplay.textContent = formattedDate;
                    
                    if (diffDays < 1) {
                        // Просрочено
                        expirationBox.className = 'expiration-box expired';
                        dateDisplay.className = 'expiration-date expired-date';
                        daysCount.textContent = `Просрочено ${Math.abs(diffDays)} дн.`;
                        daysCount.className = 'days-count expired-date';
                    } else if (diffDays <= 10) {
                        // Осталось мало дней
                        expirationBox.className = 'expiration-box warning';
                        dateDisplay.className = 'expiration-date warning-date';
                        daysCount.textContent = `Осталось ${diffDays} дн.`;
                        daysCount.className = 'days-count warning-date';
                    } else {
                        // Нормальный срок
                        expirationBox.className = 'expiration-box normal';
                        dateDisplay.className = 'expiration-date normal-date';
                        daysCount.textContent = `Осталось ${diffDays} дн.`;
                        daysCount.className = 'days-count normal-date';
                    }
                }
            }
            
            // Настройка поля для даты
            setupDateInput('manufacture_date_text', 'manufacture_date', 'manufacture_date_error');
            
            // Слушатели изменений для полей срока годности
            document.getElementById('duration_value').addEventListener('input', calculateExpirationDate);
            document.getElementById('duration_unit').addEventListener('change', calculateExpirationDate);
            
            // Обработка отправки формы
            document.getElementById('add-batch-form').addEventListener('submit', function(e) {
                const manufactureDate = document.getElementById('manufacture_date').value;
                if (!manufactureDate || manufactureDate.length !== 10) {
                    e.preventDefault();
                    document.getElementById('manufacture_date_error').style.display = 'block';
                    alert('Пожалуйста, введите корректную дату изготовления в формате дд.мм.гггг');
                }
            });
        });
    </script>
</body>
</html>
'''

history_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>История - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .container {
            max-width: 100%;
            padding: 20px 15px;
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
        .items-container {
            max-height: 65vh;
            overflow-y: auto;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            background-color: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .history-item { 
            padding: 15px; 
            border-bottom: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fafafa;
            transition: all 0.2s;
        }
        .history-item:hover {
            background: #f5f5f5;
            transform: translateY(-2px);
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .item-info { 
            flex-grow: 1;
            padding-right: 15px;
        }
        .restore-btn {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #00a046;
            color: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            flex-shrink: 0;
        }
        .nav-links {
            display: flex;
            gap: 10px;
            margin: 20px 0;
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
            transition: all 0.2s;
            text-align: center;
        }
        .nav-links a:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        h1 {
            text-align: center;
            color: #00a046;
            font-weight: 500;
            margin: 0;
        }
        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .empty-history {
            text-align: center;
            padding: 30px;
            color: #9e9e9e;
            font-style: italic;
        }
        .item-title {
            font-weight: 500;
            margin-bottom: 5px;
        }
        .item-details {
            font-size: 0.9em;
            color: #616161;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
    <div class="container">
        <h1>История списанных товаров</h1>
        
        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-input" placeholder="Поиск по названию или штрих-коду...">
        </div>
        
        <div class="nav-links">
            <a href="/">На главную</a>
        </div>
        
        <div class="items-container" id="items-container">
            {% if history_items %}
                {% for item in history_items %}
                    <div class="history-item">
                        <div class="item-info">
                            <div class="item-title">{{ item['product_name'] }}</div>
                            <div class="item-details">
                                Штрих-код: {{ item['barcode'] }}<br>
                                Срок годности: {{ item['expiration_date'] }}<br>
                                Удален: {{ item['removed_date'] }}
                            </div>
                        </div>
                        <form action="/restore_from_history" method="POST" style="display: inline;">
                            <input type="hidden" name="history_id" value="{{ item['id'] }}">
                            <button type="submit" class="restore-btn" title="Восстановить">←</button>
                        </form>
                    </div>
                {% endfor %}
            {% else %}
                <div class="empty-history">
                    История списаний пуста
                </div>
            {% endif %}
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('search-input');
            const itemsContainer = document.getElementById('items-container');
            const originalItems = itemsContainer.innerHTML;
            
            searchInput.addEventListener('input', function() {
                const searchTerm = searchInput.value.toLowerCase().trim();
                
                if (!searchTerm) {
                    itemsContainer.innerHTML = originalItems;
                    return;
                }
                
                const items = itemsContainer.querySelectorAll('.history-item');
                let hasVisibleItems = false;
                let visibleItemsHTML = '';
                
                items.forEach(item => {
                    const itemText = item.textContent.toLowerCase();
                    if (itemText.includes(searchTerm)) {
                        item.style.display = 'flex';
                        hasVisibleItems = true;
                        visibleItemsHTML += item.outerHTML;
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                if (!hasVisibleItems) {
                    itemsContainer.innerHTML = `<div class="empty-history">
                        Ничего не найдено по запросу: "${searchTerm}"
                    </div>`;
                }
            });
        });
    </script>
</body>
</html>
'''

assortment_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ассортимент - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
            position: relative;
        }
        .back-btn {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 24px;
            text-decoration: none;
            font-weight: bold;
            z-index: 10;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .container {
            max-width: 100%;
            padding: 20px 15px;
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
        .items-container {
            max-height: 65vh;
            overflow-y: auto;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            background-color: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .product-item { 
            padding: 15px; 
            border-bottom: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fafafa;
            transition: all 0.2s;
            position: relative;
        }
        .product-item:hover {
            background: #f5f5f5;
            transform: translateY(-2px);
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .item-info { 
            flex-grow: 1;
            padding-right: 80px; /* Увеличено место для кнопок */
            max-width: calc(100% - 100px); /* Увеличено место для кнопок */
            word-wrap: break-word;
        }
        .product-actions {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 8px; /* Увеличено расстояние между кнопками */
        }
        .action-btn {
            width: 40px; /* Увеличена ширина кнопок */
            height: 40px; /* Увеличена высота кнопок */
            border-radius: 50%;
            background: #f0f0f0;
            color: #333;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px; /* Увеличен размер иконок */
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .add-btn { 
            background: #00a046;
            color: white;
        }
        .edit-btn { 
            background: #ffc107;
            color: #333;
        }
        .delete-btn { 
            background: #f44336;
            color: white;
        }
        .nav-links {
            display: flex;
            gap: 10px;
            margin: 20px 0;
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
            transition: all 0.2s;
            text-align: center;
        }
        .nav-links a:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        h1 {
            text-align: center;
            color: #00a046;
            font-weight: 500;
            margin: 0;
        }
        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .empty-assortment {
            text-align: center;
            padding: 30px;
            color: #9e9e9e;
            font-style: italic;
        }
        .item-title {
            font-weight: 500;
            margin-bottom: 5px;
            font-size: 1.1em; /* Увеличен размер текста */
        }
        .item-details {
            font-size: 0.95em; /* Увеличен размер текста */
            color: #616161;
        }
        .batch-count {
            display: inline-block;
            padding: 4px 10px; /* Увеличен размер бейджа */
            background: #e0f7fa;
            border-radius: 12px;
            font-size: 0.85em;
            margin-top: 8px; /* Увеличен отступ */
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="back-btn">←</a>
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
    <div class="container">
        <h1>Ассортимент товаров</h1>
        
        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-input" placeholder="Поиск по названию или штрих-коду...">
        </div>
        
        <div class="nav-links">
            <a href="/scan">Сканировать</a>
            <a href="/history">История</a>
        </div>
        
        <div class="items-container" id="items-container">
            {% if products %}
                {% for product in products %}
                    <div class="product-item">
                        <div class="item-info">
                            <div class="item-title">{{ product['name'] }}</div>
                            <div class="item-details">
                                Штрих-код: {{ product['barcode'] }}
                                <div class="batch-count">
                                    Сроков: {{ product['batch_count'] }}
                                </div>
                            </div>
                        </div>
                        <div class="product-actions">
                            <a href="/add_batch?barcode={{ product['barcode'] }}" class="action-btn add-btn" title="Добавить срок годности">+</a>
                            <a href="/edit_product?product_id={{ product['id'] }}" class="action-btn edit-btn" title="Редактировать">✎</a>
                            <form action="/delete_product" method="POST">
                                <input type="hidden" name="product_id" value="{{ product['id'] }}">
                                <button type="submit" class="action-btn delete-btn" title="Удалить">🗑</button>
                            </form>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="empty-assortment">
                    Ассортимент пуст
                </div>
            {% endif %}
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('search-input');
            const itemsContainer = document.getElementById('items-container');
            const originalItems = itemsContainer.innerHTML;
            
            searchInput.addEventListener('input', function() {
                const searchTerm = searchInput.value.toLowerCase().trim();
                
                if (!searchTerm) {
                    itemsContainer.innerHTML = originalItems;
                    return;
                }
                
                const items = itemsContainer.querySelectorAll('.product-item');
                let hasVisibleItems = false;
                let visibleItemsHTML = '';
                
                items.forEach(item => {
                    const itemText = item.textContent.toLowerCase();
                    if (itemText.includes(searchTerm)) {
                        item.style.display = 'flex';
                        hasVisibleItems = true;
                        visibleItemsHTML += item.outerHTML;
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                if (!hasVisibleItems) {
                    itemsContainer.innerHTML = `<div class="empty-assortment">
                        Ничего не найдено по запросу: "${searchTerm}"
                    </div>`;
                }
            });
        });
    </script>
</body>
</html>
'''

edit_batch_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Редактировать срок - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            min-height: 100vh;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
            position: relative;
        }
        .back-btn {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 24px;
            text-decoration: none;
            font-weight: bold;
            z-index: 10;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .container {
            max-width: 500px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .form-container {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        h1 {
            text-align: center;
            color: #00a046;
            font-weight: 500;
            margin-top: 0;
            margin-bottom: 25px;
        }
        .product-info {
            background: #f5f5f5;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .product-name {
            font-size: 1.2em;
            font-weight: 500;
            margin-bottom: 5px;
        }
        .product-barcode {
            color: #757575;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500;
            color: #424242;
        }
        input, button {
            width: 100%;
            box-sizing: border-box;
            padding: 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: 'Roboto', sans-serif;
        }
        input:focus {
            outline: none;
            border-color: #00a046;
            box-shadow: 0 0 0 2px rgba(0, 160, 70, 0.2);
        }
        button { 
            background: #00a046;
            color: white;
            border: none;
            font-weight: 500;
            font-size: 1.1em;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
        }
        .date-input-group {
            position: relative;
        }
        .date-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #757575;
            pointer-events: none;
            font-size: 1.2em;
        }
        .date-input {
            padding-left: 40px;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="back-btn">←</a>
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h1>Редактирование срока годности</h1>
            
            <div class="product-info">
                <div class="product-name">{{ batch['name'] }}</div>
                <div class="product-barcode">Штрих-код: {{ batch['barcode'] }}</div>
            </div>
            
            <form method="POST">
                <input type="hidden" name="batch_id" value="{{ batch['id'] }}">
                
                <div class="form-group">
                    <label>Срок годности (дд.мм.гггг):</label>
                    <div class="date-input-group">
                        <span class="date-icon">📅</span>
                        <input type="hidden" id="expiration_date" name="expiration_date" value="{{ batch['expiration_date'] }}">
                        <input type="text" id="expiration_date_text" class="date-input" 
                               placeholder="дд.мм.гггг" value="{{ batch['expiration_date'] }}" required>
                    </div>
                </div>
                
                <button type="submit">Сохранить изменения</button>
            </form>
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const textField = document.getElementById('expiration_date_text');
            const hiddenField = document.getElementById('expiration_date');
            
            // Преобразуем формат даты из YYYY-MM-DD в DD.MM.YYYY
            const dbDate = hiddenField.value;
            if (dbDate) {
                const [year, month, day] = dbDate.split('-');
                textField.value = `${day}.${month}.${year}`;
            }
            
            textField.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 8) value = value.substr(0, 8);
                
                let formatted = '';
                for (let i = 0; i < value.length; i++) {
                    if (i === 2 || i === 4) formatted += '.';
                    formatted += value[i];
                }
                e.target.value = formatted;
                
                if (formatted.length === 10) {
                    const parts = formatted.split('.');
                    if (parts.length === 3) {
                        const [day, month, year] = parts;
                        hiddenField.value = `${year}-${month}-${day}`;
                    }
                }
            });
            
            textField.addEventListener('keydown', function(e) {
                if ([46, 8, 9, 27, 13].includes(e.keyCode) || 
                    (e.keyCode === 65 && e.ctrlKey === true) || 
                    (e.keyCode === 67 && e.ctrlKey === true) || 
                    (e.keyCode === 86 && e.ctrlKey === true) || 
                    (e.keyCode === 88 && e.ctrlKey === true) || 
                    (e.keyCode >= 35 && e.keyCode <= 39)) {
                    return;
                }
                
                if ((e.keyCode < 48 || e.keyCode > 57) && (e.keyCode < 96 || e.keyCode > 105)) {
                    e.preventDefault();
                }
            });
        });
    </script>
</body>
</html>
'''

edit_product_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Редактировать товар - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            min-height: 100vh;
        }
        .header {
            background-color: #00a046;
            color: white;
            padding: 15px 20px;
            text-align: center;
            position: relative;
        }
        .back-btn {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 24px;
            text-decoration: none;
            font-weight: bold;
            z-index: 10;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .container {
            max-width: 500px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .form-container {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        h1 {
            text-align: center;
            color: #00a046;
            font-weight: 500;
            margin-top: 0;
            margin-bottom: 25px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500;
            color: #424242;
        }
        input, button {
            width: 100%;
            box-sizing: border-box;
            padding: 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: 'Roboto', sans-serif;
        }
        input:focus {
            outline: none;
            border-color: #00a046;
            box-shadow: 0 0 0 2px rgba(0, 160, 70, 0.2);
        }
        button { 
            background: #00a046;
            color: white;
            border: none;
            font-weight: 500;
            font-size: 1.1em;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/assortment" class="back-btn">←</a>
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h1>Редактирование товара</h1>
            
            <form method="POST">
                <input type="hidden" name="product_id" value="{{ product['id'] }}">
                
                <div class="form-group">
                    <label>Штрих-код:</label>
                    <input type="text" name="barcode" value="{{ product['barcode'] }}" required>
                </div>
                
                <div class="form-group">
                    <label>Название товара:</label>
                    <input type="text" name="name" value="{{ product['name'] }}" required>
                </div>
                
                <button type="submit">Сохранить изменения</button>
            </form>
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>
</body>
</html>
'''

# Создаем словарь шаблонов
templates = {
    'index.html': index_html,
    'scan.html': scan_html,
    'new_product.html': new_product_html,
    'add_batch.html': add_batch_html,
    'assortment.html': assortment_html,
    'history.html': history_html,
    'edit_batch.html' : edit_batch_html,
    'edit_product.html' : edit_product_html
}

def render_template(template_name, **context):
    """Кастомная функция рендеринга шаблонов"""
    return render_template_string(templates[template_name], **context)
