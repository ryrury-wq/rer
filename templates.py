from flask import render_template_string

# Главная страница
index_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Контроль сроков</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
            overflow-x: hidden;
        }
        .items-container {
            max-height: 65vh;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        .item { 
            padding: 10px; 
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .item-info { flex-grow: 1; }
        .move-btn {
            width: 24px;
            height: 24px;
            border: 1px solid #999;
            background: white;
            cursor: pointer;
            margin-left: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .expired { background-color: #ffdddd; }
        .warning { background-color: #ffcc99; }
        .soon { background-color: #ffffcc; }
        .normal { background-color: white; }
        .nav-links {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        .nav-links a {
            padding: 8px 12px;
            background: #f0f0f0;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
        }
        h1 {
            font-size: 1.5em;
            margin: 0 0 10px 0;
        }
    </style>
</head>
<body>
    <h1>Товары с истекающим сроком</h1>
    <div class="nav-links">
        <a href="/scan">Сканировать</a>
        <a href="/history">История</a>
    </div>
    <hr>
    <div class="items-container">
        {% for item in items %}
            <div class="item {{ item.status }}">
                <div class="item-info">
                    <strong>{{ item.name }}</strong> ({{ item.barcode }})<br>
                    Годен до: {{ item.expiration_date }}<br>
                    
                    {% if item.days_since_expiry > 0 %}
                        Просрочено на : {{ item.days_since_expiry }} дня(дней)
                        <br>Удаление через: {{ item.days_until_removal }} дней
                    {% else %}
                        До истечения: {{ item.days_until_expiry }} дней
                        <br>Удаление через: {{ item.days_until_removal }} дней ({{ item.removal_date }})
                    {% endif %}
                </div>
                <form action="/move_to_history" method="POST" style="display: inline;">
                    <input type="hidden" name="batch_id" value="{{ item.id }}">
                    <button type="submit" class="move-btn" title="Переместить в историю">→</button>
                </form>
            </div>
        {% else %}
            <p>Нет товаров с истекающим сроком</p>
        {% endfor %}
    </div>
</body>
</html>
'''

scan_html = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Сканирование</title>
    <style>
        body { 
            font-family: sans-serif; 
            padding: 10px; 
            margin: 0; 
            background: #f9f9f9; 
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
            min-height: 100vh;
        }
        .scanner-container { 
            position: relative; 
            width: 300px; /* Фиксированная ширина */
            height: 200px; /* Фиксированная высота */
            margin: 0 auto 15px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
            width: 90%; 
            height: 60%;
            border: 2px dashed red; 
            border-radius: 8px; 
            pointer-events: none; 
            box-sizing: border-box;
        }
        form { 
            width: 90%;
            max-width: 400px;
            margin-top: 10px; 
        }
        input[type="text"], input[type="date"], input[type="number"], select {
            width: 100%; 
            padding: 12px; 
            font-size: 1em; 
            border: 1px solid #ccc;
            border-radius: 4px; 
            margin-bottom: 10px; 
            background: #fff; 
            box-sizing: border-box;
        }
        button { 
            width: 100%; 
            padding: 12px; 
            background-color: #28a745; 
            color: white;
            font-size: 1.1em; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
            margin-top: 10px;
        }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        .camera-error {
            color: red;
            text-align: center;
            padding: 10px;
        }
        .camera-controls {
            margin-top: 10px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .camera-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border-radius: 4px;
            border: 1px solid #ccc;
            cursor: pointer;
            color: black;
        }
        .beep {
            display: none;
        }
        .manual-input {
            margin-top: 10px;
            text-align: center;
        }
        .manual-input a {
            color: #0066cc;
            text-decoration: none;
        }
        
        /* Стиль для поля даты */
        #manufacture_date_display {
            font-family: monospace;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
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
            <label for="manufacture_date_display">Дата изготовления:</label>
            <!-- Видимое поле для ввода пользователя -->
            <input type="text" 
                   id="manufacture_date_display" 
                   placeholder="мм.дд.гггг" 
                   required
                   maxlength="10">
            <!-- Скрытое поле для отправки на сервер -->
            <input type="hidden" 
                   name="manufacture_date" 
                   id="manufacture_date">
        </div>

        <div class="form-group">
            <label>Срок годности:</label>
            <div style="display: flex; gap: 10px;">
                <input type="number" name="duration_value" required style="flex: 2;">
                <select name="duration_unit" style="flex: 1;">
                    <option value="days">дней</option>
                    <option value="months">месяцев</option>
                    <option value="years">лет</option>
                </select>
            </div>
        </div>

        <button type="submit">Сохранить</button>
    </form>

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
        const dateDisplay = document.getElementById('manufacture_date_display'); // Видимое поле
        const dateInput = document.getElementById('manufacture_date'); // Скрытое поле
        
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
        
        // Обработчик для автоматического форматирования даты
        dateDisplay.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 4) {
                value = value.substring(0, 2) + '.' + value.substring(2, 4) + '.' + value.substring(4, 8);
            } else if (value.length > 2) {
                value = value.substring(0, 2) + '.' + value.substring(2, 4);
            }
            
            e.target.value = value;
        });

        // Функция преобразования даты в ISO формат
        function convertToISODate(dateString) {
            const parts = dateString.split('.');
            if (parts.length !== 3) return null;
            
            const [month, day, year] = parts;
            return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        }
        
        // Отправка формы
        scannerForm.addEventListener('submit', (e) => {
            if (!barcodeInput.value) {
                e.preventDefault();
                alert("Пожалуйста, введите или отсканируйте штрих-код");
                barcodeInput.focus();
                return;
            }
            
            // Проверка формата даты
            const dateRegex = /^\d{2}\.\d{2}\.\d{4}$/;
            if (!dateRegex.test(dateDisplay.value)) {
                e.preventDefault();
                alert('Пожалуйста, введите дату в формате мм.дд.гггг');
                dateDisplay.focus();
                dateDisplay.select();
                return;
            }
            
            // Преобразуем в ISO формат для сервера
            const isoDate = convertToISODate(dateDisplay.value);
            if (!isoDate) {
                e.preventDefault();
                alert('Неверный формат даты');
                dateDisplay.focus();
                dateDisplay.select();
                return;
            }
            
            // Записываем ISO дату в скрытое поле
            dateInput.value = isoDate;
        });
    </script>
</body>
</html>
'''

# Обновим остальные шаблоны аналогично
new_product_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Новый товар</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
        }
        form {
            max-width: 400px;
            margin: 0 auto;
        }
        input, button { 
            width: 100%;
            box-sizing: border-box;
            padding: 12px; 
            margin: 5px 0; 
        }
        h1 {
            font-size: 1.5em;
        }
    </style>
</head>
<body>
    <h1>Добавление нового товара</h1>
    <form method="POST">
        <label>Штрих-код:</label>
        <input type="text" name="barcode" value="{{ barcode }}" readonly>
        <label>Название товара:</label>
        <input type="text" name="name" required>
        <button type="submit">Сохранить</button>
    </form>
</body>
</html>
'''

add_batch_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Добавить срок</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
        }
        form {
            max-width: 400px;
            margin: 0 auto;
        }
        input, button { 
            width: 100%;
            box-sizing: border-box;
            padding: 12px; 
            margin: 5px 0; 
        }
        h1 {
            font-size: 1.5em;
        }
    </style>
</head>
<body>
    <h1>Добавление срока годности для: {{ product_name }}</h1>
    <form method="POST">
        <label>Срок годности:</label>
        <input type="date" name="expiration_date" required>
        <button type="submit">Добавить</button>
    </form>
</body>
</html>
'''

history_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>История</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 10px;
            padding: 0;
        }
        .items-container {
            max-height: 70vh;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        li { 
            padding: 8px; 
            border-bottom: 1px solid #eee; 
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .item-info { flex-grow: 1; }
        .restore-btn {
            width: 24px;
            height: 24px;
            border: 1px solid #999;
            background: white;
            cursor: pointer;
            margin-left: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .nav-links {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        .nav-links a {
            padding: 8px 12px;
            background: #f0f0f0;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
        }
        h1 {
            font-size: 1.5em;
            margin: 0 0 10px 0;
        }
    </style>
</head>
<body>
    <h1>История списанных товаров</h1>
    <div class="nav-links">
        <a href="/">На главную</a>
    </div>
    <hr>
    <div class="items-container">
        <ul>
            {% for item in history_items %}
                <li>
                    <div class="item-info">
                        <strong>{{ item['product_name'] }}</strong> ({{ item['barcode'] }})<br>
                        Срок годности: {{ item['expiration_date'] }}<br>
                        Удален: {{ item['removed_date'] }}
                    </div>
                    <form action="/restore_from_history" method="POST" style="display: inline;">
                        <input type="hidden" name="history_id" value="{{ item['id'] }}">
                        <button type="submit" class="restore-btn" title="Восстановить">←</button>
                    </form>
                </li>
            {% else %}
                <li>История пуста</li>
            {% endfor %}
        </ul>
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
