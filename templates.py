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
            background-color: #00a046; /* Зеленый Вкусвилл */
            color: white;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            padding: 15px;
        }
        .items-container {
            max-height: 60vh;
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
        }
        .item:hover {
            box-shadow: 0 2px 6px rgba(0,160,70,0.15);
            transform: translateY(-2px);
        }
        .item-info { flex-grow: 1; }
        .move-btn {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #00a046;
            color: white;
            border: none;
            cursor: pointer;
            margin-left: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
        }
        .expired { 
            background-color: #ffebee;
            border-left: 4px solid #f44336;
        }
        .warning { 
            background-color: #fff8e1;
            border-left: 4px solid #ffc107;
        }
        .soon { 
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
        }
        .normal { 
            background-color: white;
            border-left: 4px solid #e0e0e0;
        }
        .nav-links {
            display: flex;
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
            transition: all 0.2s;
            text-align: center;
            flex: 1;
            max-width: 45%;
        }
        .nav-links a:hover {
            background: #008c3a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        h1 {
            font-size: 1.5em;
            margin: 0 0 10px 0;
            text-align: center;
            color: #00a046;
            font-weight: 500;
        }
        .footer {
            text-align: center;
            padding: 20px 15px 10px;
            color: #757575;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
            margin-top: 5px;
        }
        .expired-badge { background: #ffcdd2; color: #c62828; }
        .warning-badge { background: #ffecb3; color: #ff8f00; }
        .soon-badge { background: #c8e6c9; color: #2e7d32; }
        .normal-badge { background: #e0e0e0; color: #424242; }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
    <div class="container">
        <h1>Товары с истекающим сроком</h1>
        
        <div class="nav-links">
            <a href="/scan">Сканировать</a>
            <a href="/history">История</a>
        </div>
        
        <div class="items-container">
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
                    <form action="/move_to_history" method="POST" style="display: inline;">
                        <input type="hidden" name="batch_id" value="{{ item.id }}">
                        <button type="submit" class="move-btn" title="Переместить в историю">→</button>
                    </form>
                </div>
            {% else %}
                <div style="text-align:center; padding:30px; color:#757575">
                    Нет товаров с истекающим сроком
                </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>
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
    </style>
</head>
<body>
    <div class="header">
        <h1 class="logo">Вкусвилл</h1>
    </div>
    
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
                        <input type="date" name="manufacture_date" id="manufacture_date" style="display: none">
                        <input type="text" id="manufacture_date_text" placeholder="дд.мм.гггг" required>
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
        
        // Функция для остановки текущего потока
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
        
        // Функция для запуска камеры
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
        
        // Проверка поддержки фонарика
        function checkTorchSupport() {
            torchBtn.style.display = 'none';
            if (currentStream) {
                const track = currentStream.getVideoTracks()[0];
                if (track && track.getCapabilities().torch) {
                    torchBtn.style.display = 'block';
                }
            }
        }
        
        // Переключение фонарика
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
        
        // Функция для запуска сканера
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
        
        // Функция для остановки сканера
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
        
        // Перезапуск камеры
        restartBtn.addEventListener('click', () => {
            startCamera();
        });
        
        // Управление фонариком
        torchBtn.addEventListener('click', toggleTorch);
        
        // Ручной ввод штрих-кода
        manualInputLink.addEventListener('click', (e) => {
            e.preventDefault();
            barcodeInput.removeAttribute('readonly');
            barcodeInput.focus();
            barcodeInput.placeholder = "Введите штрих-код вручную";
        });
        
        // Обработка изменения видимости страницы
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopScanner();
            } else {
                scannerActive = true;
                startScanner();
            }
        });
        
        // Проверяем поддержку медиаустройств
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showCameraError();
            cameraError.textContent = "Ваш браузер не поддерживает доступ к камере";
        } else {
            startCamera();
        }
        
        // Отправка формы
        scannerForm.addEventListener('submit', (e) => {
            if (!barcodeInput.value) {
                e.preventDefault();
                alert("Пожалуйста, введите или отсканируйте штрих-код");
                barcodeInput.focus();
            }
        });
    </script>

    <!-- Скрипт для работы с датой -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const dateField = document.getElementById('manufacture_date');
            const textField = document.getElementById('manufacture_date_text');
            
            // Автозаполнение точек и форматирование
            textField.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 8) value = value.substr(0, 8);
                
                let formatted = '';
                for (let i = 0; i < value.length; i++) {
                    if (i === 2 || i === 4) formatted += '.';
                    formatted += value[i];
                }
                e.target.value = formatted;
                
                // Обновление скрытого поля даты
                if (formatted.length === 10) {
                    const parts = formatted.split('.');
                    if (parts.length === 3) {
                        const [day, month, year] = parts;
                        dateField.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                    }
                }
            });
            
            // Валидация формата даты
            textField.addEventListener('blur', function() {
                const value = textField.value;
                if (value.length > 0 && value.length < 10) {
                    alert('Пожалуйста, введите полную дату в формате дд.мм.гггг');
                    textField.focus();
                }
            });
            
            // Обработка клавиш для удобства ввода
            textField.addEventListener('keydown', function(e) {
                // Разрешаем: backspace, delete, tab, escape, enter
                if ([46, 8, 9, 27, 13].includes(e.keyCode) || 
                    // Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
                    (e.keyCode === 65 && e.ctrlKey === true) || 
                    (e.keyCode === 67 && e.ctrlKey === true) || 
                    (e.keyCode === 86 && e.ctrlKey === true) || 
                    (e.keyCode === 88 && e.ctrlKey === true) || 
                    // Стрелки вправо/влево
                    (e.keyCode >= 35 && e.keyCode <= 39)) {
                    return;
                }
                
                // Запрещаем все, кроме цифр
                if ((e.keyCode < 48 || e.keyCode > 57) && (e.keyCode < 96 || e.keyCode > 105)) {
                    e.preventDefault();
                }
            });
            
            // Проверка даты перед отправкой формы
            scannerForm.addEventListener('submit', function(e) {
                if (!dateField.value) {
                    e.preventDefault();
                    alert('Пожалуйста, введите корректную дату изготовления в формате дд.мм.гггг');
                    textField.focus();
                }
            });
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
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 25px;
            padding: 12px;
            background: #e8f5e9;
            border-radius: 8px;
            font-weight: 500;
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
            <h1>Добавление срока годности</h1>
            <div class="product-name">{{ product_name }}</div>
            <form method="POST">
                <div class="form-group">
                    <label>Срок годности:</label>
                    <input type="date" name="expiration_date" required>
                </div>
                <button type="submit">Добавить срок</button>
            </form>
        </div>
    </div>
    
    <div class="footer">
        Сделано М2(Shevchenko) by Bekeshnyuk
    </div>
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
        
        <div class="nav-links">
            <a href="/">На главную</a>
        </div>
        
        <div class="items-container">
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
