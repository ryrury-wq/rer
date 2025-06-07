from flask import render_template_string

# Общие стили для всех страниц
common_styles = '''
    <style>
        :root {
            --vkusvill-green: #43A047;
            --vkusvill-light-green: #E8F5E9;
            --vkusvill-dark-green: #388E3C;
            --vkusvill-light: #F5F5F5;
            --vkusvill-accent-orange: #FF9800;
            --vkusvill-accent-red: #F44336;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Open Sans', 'Arial', sans-serif;
            background-color: #FFFFFF;
            color: #333333;
            line-height: 1.6;
            max-width: 100%;
            overflow-x: hidden;
            padding: 0;
            margin: 0;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 15px;
        }
        
        header {
            background-color: white;
            padding: 15px 0;
            border-bottom: 1px solid #E0E0E0;
            text-align: center;
            margin-bottom: 15px;
        }
        
        .logo {
            height: 40px;
            margin-bottom: 5px;
        }
        
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 10px 0;
            flex-wrap: wrap;
        }
        
        .nav-links a {
            padding: 8px 15px;
            background: var(--vkusvill-light-green);
            border-radius: 20px;
            text-decoration: none;
            color: var(--vkusvill-dark-green);
            font-weight: 600;
            font-size: 0.9em;
            border: 1px solid rgba(67, 160, 71, 0.2);
            transition: all 0.2s;
        }
        
        .nav-links a:hover {
            background: var(--vkusvill-green);
            color: white;
        }
        
        h1, h2, h3 {
            color: var(--vkusvill-dark-green);
            margin-bottom: 15px;
            text-align: center;
        }
        
        h1 {
            font-size: 1.6rem;
        }
        
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #EEEEEE;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 20px;
            background-color: var(--vkusvill-green);
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            transition: background-color 0.2s;
            width: 100%;
        }
        
        .btn:hover {
            background-color: var(--vkusvill-dark-green);
        }
        
        .btn-warning {
            background-color: var(--vkusvill-accent-orange);
        }
        
        .btn-danger {
            background-color: var(--vkusvill-accent-red);
        }
        
        form {
            width: 100%;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            font-size: 1rem;
        }
        
        input:focus, select:focus {
            border-color: var(--vkusvill-green);
            outline: none;
            box-shadow: 0 0 0 2px rgba(67, 160, 71, 0.2);
        }
        
        footer {
            text-align: center;
            padding: 20px 0;
            color: #757575;
            font-size: 0.85rem;
            margin-top: 30px;
            border-top: 1px solid #EEEEEE;
        }
        
        .status-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 5px;
        }
        
        .expired .status-badge { background: #FFEBEE; color: var(--vkusvill-accent-red); }
        .warning .status-badge { background: #FFF3E0; color: var(--vkusvill-accent-orange); }
        .soon .status-badge { background: #FFFDE7; color: #FBC02D; }
        .normal .status-badge { background: #E8F5E9; color: var(--vkusvill-dark-green); }
    </style>
'''

# Логотип Вкусвилла в формате base64 (упрощенный вариант)
vkusvill_logo = '''
<svg class="logo" viewBox="0 0 200 40" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="40" fill="white"/>
    <text x="20" y="25" font-family="Arial" font-size="18" fill="#43A047">ВКУСВИЛЛ</text>
</svg>
'''

footer_html = '''
<footer>
    Сделано M2 (Shevchenko) by Bekeshnyuk
</footer>
'''

# Главная страница
index_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Контроль сроков - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    {common_styles}
    <style>
        .items-container {{
            max-height: 55vh;
            overflow-y: auto;
            margin-top: 10px;
        }}
        
        .item {{
            padding: 12px;
            border-bottom: 1px solid #EEEEEE;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.2s;
        }}
        
        .item:hover {{
            background-color: #F9F9F9;
        }}
        
        .item-info {{ 
            flex-grow: 1;
            font-size: 0.95rem;
        }}
        
        .item-info strong {{
            color: var(--vkusvill-dark-green);
            display: flex;
            align-items: center;
        }}
        
        .move-btn {{
            width: 32px;
            height: 32px;
            background: var(--vkusvill-green);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            margin-left: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }}
        
        .move-btn:hover {{
            background: var(--vkusvill-dark-green);
        }}
        
        .date-info {{
            margin-top: 5px;
            font-size: 0.85rem;
            color: #616161;
        }}
        
        .no-items {{
            text-align: center;
            padding: 20px;
            color: #9E9E9E;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            {vkusvill_logo}
            <h1>Товары с истекающим сроком</h1>
        </header>
        
        <div class="nav-links">
            <a href="/scan">Сканировать</a>
            <a href="/history">История</a>
        </div>
        
        <div class="card">
            <div class="items-container">
                {% for item in items %}
                    <div class="item {{ item.status }}">
                        <div class="item-info">
                            <strong>{{ item.name }} <span class="status-badge">{{ item.status_label }}</span></strong>
                            <div class="date-info">
                                Штрих-код: {{ item.barcode }}<br>
                                Годен до: {{ item.expiration_date }}<br>
                                
                                {% if item.days_since_expiry > 0 %}
                                    Просрочено на: {{ item.days_since_expiry }} дн.
                                    <br>Удаление через: {{ item.days_until_removal }} дн.
                                {% else %}
                                    До истечения: {{ item.days_until_expiry }} дн.
                                    <br>Удаление через: {{ item.days_until_removal }} дн.
                                {% endif %}
                            </div>
                        </div>
                        <form action="/move_to_history" method="POST" style="display: inline;">
                            <input type="hidden" name="batch_id" value="{{ item.id }}">
                            <button type="submit" class="move-btn" title="Переместить в историю">→</button>
                        </form>
                    </div>
                {% else %}
                    <div class="no-items">Нет товаров с истекающим сроком</div>
                {% endfor %}
            </div>
        </div>
        
        {footer_html}
    </div>
</body>
</html>
'''

scan_html = f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Сканирование - Вкусвилл</title>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    {common_styles}
    <style>
        .scanner-container {{ 
            position: relative; 
            width: 100%;
            height: 250px;
            margin: 0 auto 15px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            background: black;
        }}
        
        video {{ 
            width: 100%; 
            height: 100%; 
            object-fit: cover;
        }}
        
        .overlay {{ 
            position: absolute; 
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80%; 
            height: 50%;
            border: 2px solid var(--vkusvill-green); 
            border-radius: 8px; 
            pointer-events: none; 
            box-sizing: border-box;
            box-shadow: 0 0 0 1000px rgba(0, 0, 0, 0.5);
        }}
        
        .camera-controls {{
            display: flex;
            gap: 10px;
            margin: 15px 0;
            justify-content: center;
        }}
        
        .camera-btn {{
            padding: 10px 15px;
            background: var(--vkusvill-light-green);
            border-radius: 20px;
            border: 1px solid rgba(67, 160, 71, 0.3);
            cursor: pointer;
            color: var(--vkusvill-dark-green);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .camera-btn:hover {{
            background: var(--vkusvill-green);
            color: white;
        }}
        
        .manual-input {{
            text-align: center;
            margin: 10px 0;
        }}
        
        .manual-input a {{
            color: var(--vkusvill-green);
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        
        .form-group {{
            margin-bottom: 15px;
        }}
        
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: var(--vkusvill-dark-green);
        }}
        
        .duration-group {{
            display: flex;
            gap: 10px;
        }}
        
        .duration-group input {{
            flex: 2;
        }}
        
        .duration-group select {{
            flex: 1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            {vkusvill_logo}
            <h1>Сканирование товара</h1>
        </header>
        
        <div class="card">
            <div class="scanner-container">
                <video id="video" autoplay playsinline muted></video>
                <div class="overlay"></div>
                <div id="camera-error" class="camera-error" style="display: none; text-align: center; padding: 20px; color: #F44336;">
                    Ошибка доступа к камере. Проверьте разрешения.
                </div>
            </div>

            <div class="camera-controls">
                <button id="restart-btn" class="camera-btn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
                    Перезапустить
                </button>
                <button id="torch-btn" class="camera-btn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 2v6l4 4-4 4v6l12-9L6 2z"/></svg>
                    Фонарик
                </button>
            </div>

            <div class="manual-input">
                <a href="#" id="manual-input-link">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 5v14H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-8 12H9v-2h2v2zm0-4H9V9h2v2zm4 4h-2v-2h2v2zm0-4h-2V9h2v2z"/></svg>
                    Ввести штрих-код вручную
                </a>
            </div>

            <audio id="beep" class="beep" src="https://assets.mixkit.co/sfx/preview/mixkit-electronic-retail-scanner-beep-1083.mp3" preload="auto"></audio>

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
                    <label for="manufacture_date">Дата изготовления:</label>
                    <input type="date" name="manufacture_date" required>
                </div>

                <div class="form-group">
                    <label>Срок годности:</label>
                    <div class="duration-group">
                        <input type="number" name="duration_value" required placeholder="Количество">
                        <select name="duration_unit">
                            <option value="days">дней</option>
                            <option value="months">месяцев</option>
                            <option value="years">лет</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="btn">Сохранить товар</button>
            </form>
        </div>
        
        {footer_html}
    </div>

    <script type="module">
        import {{ BrowserMultiFormatReader }} from 'https://cdn.jsdelivr.net/npm/@zxing/browser@0.0.10/+esm';

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
        
        // Функция для остановки текущего потока
        function stopCurrentStream() {{
            if (currentStream) {{
                currentStream.getTracks().forEach(track => {{
                    if (track.kind === 'video' && torchOn) {{
                        track.applyConstraints({{ advanced: [{{ torch: false }}] }});
                    }}
                    track.stop();
                }});
                currentStream = null;
                torchOn = false;
                torchBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 2v6l4 4-4 4v6l12-9L6 2z"/></svg> Фонарик';
            }}
        }}
        
        // Функция для запуска камеры
        async function startCamera() {{
            try {{
                stopCurrentStream();
                
                const constraints = {{
                    video: {{
                        facingMode: 'environment',
                        width: {{ ideal: 1280 }},
                        height: {{ ideal: 720 }},
                        focusMode: 'continuous'
                    }}
                }};
                
                currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = currentStream;
                
                cameraError.style.display = 'none';
                video.style.display = 'block';
                
                checkTorchSupport();
                startScanner();
            }} catch (err) {{
                console.error("Ошибка доступа к камере:", err);
                showCameraError();
            }}
        }}
        
        // Проверка поддержки фонарика
        function checkTorchSupport() {{
            torchBtn.style.display = 'none';
            if (currentStream) {{
                const track = currentStream.getVideoTracks()[0];
                if (track && track.getCapabilities().torch) {{
                    torchBtn.style.display = 'flex';
                }}
            }}
        }}
        
        // Переключение фонарика
        async function toggleTorch() {{
            if (!currentStream) return;
            
            const track = currentStream.getVideoTracks()[0];
            if (!track || !track.getCapabilities().torch) return;
            
            try {{
                await track.applyConstraints({{
                    advanced: [{{ torch: !torchOn }}]
                }});
                torchOn = !torchOn;
                torchBtn.innerHTML = torchOn 
                    ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 2v6l4 4-4 4v6l12-9L6 2z"/></svg> Выкл. фонарик' 
                    : '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 2v6l4 4-4 4v6l12-9L6 2z"/></svg> Фонарик';
            }} catch (err) {{
                console.error("Ошибка переключения фонарика:", err);
            }}
        }}
        
        // Функция для запуска сканера
        function startScanner() {{
            if (!scannerActive) return;
            
            codeReader.decodeFromVideoElement(video, (result, err) => {{
                if (!scannerActive) return;
                
                const now = Date.now();
                if (now - lastScanTime < SCAN_COOLDOWN) return;
                
                if (result) {{
                    lastScanTime = now;
                    
                    if (beepSound) {{
                        beepSound.currentTime = 0;
                        beepSound.play().catch(e => console.log("Не удалось воспроизвести звук:", e));
                    }}
                    
                    barcodeInput.value = result.text;
                    document.getElementById('name').focus();
                    
                    fetch(`/get-product-name?barcode=${{result.text}}`)
                        .then(res => res.json())
                        .then(data => {{
                            if (data.found) {{
                                document.getElementById('name').value = data.name;
                            }}
                        }});
                }}
            }});
        }}
        
        // Функция для остановки сканера
        function stopScanner() {{
            scannerActive = false;
            codeReader.reset();
        }}
        
        function showCameraError() {{
            cameraError.style.display = 'block';
            video.style.display = 'none';
            barcodeInput.removeAttribute('readonly');
            barcodeInput.placeholder = "Введите штрих-код вручную";
        }}
        
        // Перезапуск камеры
        restartBtn.addEventListener('click', () => {{
            startCamera();
        }});
        
        // Управление фонариком
        torchBtn.addEventListener('click', toggleTorch);
        
        // Ручной ввод штрих-кода
        manualInputLink.addEventListener('click', (e) => {{
            e.preventDefault();
            barcodeInput.removeAttribute('readonly');
            barcodeInput.focus();
            barcodeInput.placeholder = "Введите штрих-код вручную";
        }});
        
        // Обработка изменения видимости страницы
        document.addEventListener('visibilitychange', () => {{
            if (document.hidden) {{
                stopScanner();
            }} else {{
                scannerActive = true;
                startScanner();
            }}
        }});
        
        // Проверяем поддержку медиаустройств
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
            showCameraError();
            cameraError.textContent = "Ваш браузер не поддерживает доступ к камере";
        }} else {{
            startCamera();
        }}
        
        // Отправка формы
        scannerForm.addEventListener('submit', (e) => {{
            if (!barcodeInput.value) {{
                e.preventDefault();
                alert("Пожалуйста, введите или отсканируйте штрих-код");
                barcodeInput.focus();
            }}
        }});
    </script>
</body>
</html>
'''

# Обновим остальные шаблоны аналогично
new_product_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Новый товар - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    {common_styles}
</head>
<body>
    <div class="container">
        <header>
            {vkusvill_logo}
            <h1>Добавление нового товара</h1>
        </header>
        
        <div class="card">
            <form method="POST">
                <div class="form-group">
                    <label>Штрих-код:</label>
                    <input type="text" name="barcode" value="{{ barcode }}" readonly>
                </div>
                
                <div class="form-group">
                    <label>Название товара:</label>
                    <input type="text" name="name" required placeholder="Введите название товара">
                </div>
                
                <button type="submit" class="btn">Сохранить товар</button>
            </form>
        </div>
        
        {footer_html}
    </div>
</body>
</html>
'''

add_batch_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Добавить срок - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    {common_styles}
</head>
<body>
    <div class="container">
        <header>
            {vkusvill_logo}
            <h1>Добавление срока годности</h1>
        </header>
        
        <div class="card">
            <h2>{{ product_name }}</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Дата окончания срока годности:</label>
                    <input type="date" name="expiration_date" required>
                </div>
                
                <button type="submit" class="btn">Добавить срок</button>
            </form>
        </div>
        
        {footer_html}
    </div>
</body>
</html>
'''

history_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>История - Вкусвилл</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    {common_styles}
    <style>
        .items-container {{
            max-height: 60vh;
            overflow-y: auto;
        }}
        
        .history-item {{
            padding: 12px;
            border-bottom: 1px solid #EEEEEE;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .history-item:hover {{
            background-color: #F9F9F9;
        }}
        
        .item-info {{ 
            flex-grow: 1;
            font-size: 0.95rem;
        }}
        
        .item-info strong {{
            color: var(--vkusvill-dark-green);
        }}
        
        .date-info {{
            margin-top: 5px;
            font-size: 0.85rem;
            color: #616161;
        }}
        
        .restore-btn {{
            width: 32px;
            height: 32px;
            background: var(--vkusvill-green);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            margin-left: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }}
        
        .restore-btn:hover {{
            background: var(--vkusvill-dark-green);
        }}
        
        .no-history {{
            text-align: center;
            padding: 20px;
            color: #9E9E9E;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            {vkusvill_logo}
            <h1>История списанных товаров</h1>
        </header>
        
        <div class="nav-links">
            <a href="/">На главную</a>
        </div>
        
        <div class="card">
            <div class="items-container">
                {% for item in history_items %}
                    <div class="history-item">
                        <div class="item-info">
                            <strong>{{ item['product_name'] }}</strong>
                            <div class="date-info">
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
                {% else %}
                    <div class="no-history">История списаний пуста</div>
                {% endfor %}
            </div>
        </div>
        
        {footer_html}
    </div>
</body>
</html>
'''

templates = {
    'index.html': index_html,
    'scan.html': scan_html,
    'new_product.html': new_product_html,
    'add_batch.html': add_batch_html,
    'history.html': history_html
}

def render_template(template_name, **context):
    return render_template_string(templates[template_name], **context)
