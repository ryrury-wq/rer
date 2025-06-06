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
            height: 100vh;
        }
        .scanner-container { 
            position: relative; 
            width: 90%; 
            max-width: 400px;
            height: 200px;
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
            height: 60%; /* Увеличена высота области сканирования */
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
        .scanner-instruction {
            text-align: center;
            margin: 10px 0 15px;
            font-size: 0.9em;
            color: #666;
        }
        .scan-tips {
            text-align: center;
            margin: 5px 0;
            font-size: 0.8em;
            color: #888;
        }
        h1 {
            font-size: 1.5em;
            margin: 5px 0 10px;
        }
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
    </style>
</head>
<body>
    <h1>Сканирование товара</h1>
    
    <div class="scanner-instruction">
        Поместите штрих-код в рамку
    </div>
    <div class="scan-tips">
        Держите устройство устойчиво на расстоянии 15-30 см от штрих-кода
    </div>

    <div class="scanner-container">
        <video id="video" autoplay playsinline muted></video>
        <div class="overlay"></div>
        <div id="camera-error" class="camera-error" style="display: none;">
            Ошибка доступа к камере. Проверьте разрешения.
        </div>
    </div>

    <div class="camera-controls">
        <button id="restart-btn" class="camera-btn">Перезапустить</button>
        <button id="switch-btn" class="camera-btn">Камера</button>
        <button id="torch-btn" class="camera-btn">Фонарик</button>
    </div>

    <audio id="beep" class="beep" src="https://assets.mixkit.co/sfx/preview/mixkit-electronic-retail-scanner-beep-1083.mp3" preload="auto"></audio>

    <form method="POST">
        <div class="form-group">
            <label for="barcode">Штрих-код:</label>
            <input type="text" name="barcode" id="barcode" readonly placeholder="Ожидание сканирования..." required>
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
        const switchBtn = document.getElementById('switch-btn');
        const torchBtn = document.getElementById('torch-btn');
        const beepSound = document.getElementById('beep');
        
        let currentStream = null;
        let usingFrontCamera = false;
        let scannerActive = true;
        let torchOn = false;
        let lastScanTime = 0;
        const SCAN_COOLDOWN = 2000; // 2 секунды между сканированиями
        
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
        async function startCamera(facingMode = 'environment') {
            try {
                stopCurrentStream();
                
                const constraints = {
                    video: {
                        facingMode: facingMode,
                        width: { ideal: 1280 }, // Более высокое разрешение
                        height: { ideal: 720 },
                        focusMode: 'continuous' // Непрерывная фокусировка
                    }
                };
                
                currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = currentStream;
                
                // Для фронтальной камеры применяем зеркальное отображение
                if (facingMode === 'user') {
                    video.style.transform = 'scaleX(-1)';
                } else {
                    video.style.transform = 'none';
                }
                
                // Запускаем сканер
                startScanner();
                
                cameraError.style.display = 'none';
                video.style.display = 'block';
                
                // Проверяем поддержку фонарика
                checkTorchSupport();
            } catch (err) {
                console.error("Ошибка доступа к камере:", err);
                showCameraError();
            }
        }
        
        // Проверка поддержки фонарика
        function checkTorchSupport() {
            if (currentStream) {
                const track = currentStream.getVideoTracks()[0];
                if (track && track.getCapabilities().torch) {
                    torchBtn.style.display = 'block';
                    return;
                }
            }
            torchBtn.style.display = 'none';
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
                const now = Date.now();
                
                // Защита от повторных сканирований
                if (now - lastScanTime < SCAN_COOLDOWN) {
                    if (scannerActive) requestAnimationFrame(() => startScanner());
                    return;
                }
                
                if (result) {
                    lastScanTime = now;
                    
                    // Звуковой сигнал
                    if (beepSound) {
                        beepSound.currentTime = 0;
                        beepSound.play().catch(e => console.log("Не удалось воспроизвести звук:", e));
                    }
                    
                    barcodeInput.value = result.text;
                    
                    // Автоматический фокус на следующее поле
                    document.getElementById('name').focus();
                    
                    // Проверка наличия товара в базе
                    fetch(`/get-product-name?barcode=${result.text}`)
                        .then(res => res.json())
                        .then(data => {
                            if (data.found) {
                                document.getElementById('name').value = data.name;
                            }
                        });
                }
                
                if (err && !(err instanceof ZXing.NotFoundException)) {
                    console.error(err);
                }
                
                // Рекурсивно продолжаем сканирование
                if (scannerActive) {
                    requestAnimationFrame(() => startScanner());
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
        }
        
        // Переключение камеры
        switchBtn.addEventListener('click', () => {
            usingFrontCamera = !usingFrontCamera;
            startCamera(usingFrontCamera ? 'user' : 'environment');
        });
        
        // Перезапуск камеры
        restartBtn.addEventListener('click', () => {
            startCamera(usingFrontCamera ? 'user' : 'environment');
        });
        
        // Управление фонариком
        torchBtn.addEventListener('click', toggleTorch);
        
        // Проверяем поддержку медиаустройств
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showCameraError();
            cameraError.textContent = "Ваш браузер не поддерживает доступ к камере";
        } else {
            startCamera();
        }
        
        // Остановка сканера при уходе со страницы
        window.addEventListener('beforeunload', () => {
            stopScanner();
            stopCurrentStream();
        });
        
        // Советы по сканированию
        setTimeout(() => {
            if (!barcodeInput.value) {
                document.querySelector('.scan-tips').textContent = 
                    "Если сканирование не работает, попробуйте поднести штрих-код ближе или дальше";
            }
        }, 5000);
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
