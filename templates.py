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
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Сканирование</title>
    <style>
        /* Оптимизированные стили */
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
            transform: none !important; /* Убрано зеркальное отражение */
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
        /* Остальные стили без изменений */
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
        <button id="switch-btn" class="camera-btn">Камера</button>
        <button id="torch-btn" class="camera-btn">Фонарик</button>
    </div>

    <div class="manual-input">
        <a href="#" id="manual-input-link">Ввести штрих-код вручную</a>
    </div>

    <audio id="beep" class="beep" src="https://assets.mixkit.co/sfx/preview/mixkit-electronic-retail-scanner-beep-1083.mp3" preload="auto"></audio>

    <form method="POST" id="scanner-form">
        <!-- Поля формы без изменений -->
    </form>

    <!-- Исправленная версия ZXing -->
    <script type="module">
        import { BrowserMultiFormatReader } from 'https://cdn.jsdelivr.net/npm/@zxing/browser@0.1.0/+esm';

        const codeReader = new BrowserMultiFormatReader();
        const video = document.getElementById('video');
        const barcodeInput = document.getElementById('barcode');
        const cameraError = document.getElementById('camera-error');
        const restartBtn = document.getElementById('restart-btn');
        const switchBtn = document.getElementById('switch-btn');
        const torchBtn = document.getElementById('torch-btn');
        const beepSound = document.getElementById('beep');
        const manualInputLink = document.getElementById('manual-input-link');
        const scannerForm = document.getElementById('scanner-form');
        
        let currentStream = null;
        let usingFrontCamera = false;
        let scannerActive = true;
        let torchOn = false;
        let lastScanTime = 0;
        let isProcessing = false; // Флаг для контроля обработки
        const SCAN_COOLDOWN = 1000; // Увеличенное время между сканированиями
        
        // Оптимизированные функции работы с камерой
        function stopCurrentStream() {
            if (currentStream) {
                scannerActive = false;
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
        
        async function startCamera(facingMode = 'environment') {
            try {
                stopCurrentStream();
                scannerActive = true;
                
                const constraints = {
                    video: {
                        facingMode: facingMode,
                        width: { ideal: 1280 }, // Снижено разрешение
                        height: { ideal: 720 },
                        frameRate: { ideal: 15, max: 30 }, // Ограничение FPS
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
        
        // Оптимизированное сканирование
        function startScanner() {
            if (!scannerActive || isProcessing) return;
            
            isProcessing = true;
            
            requestAnimationFrame(async () => {
                try {
                    const result = await codeReader.decodeFromVideoElement(video);
                    
                    if (result) {
                        const now = Date.now();
                        if (now - lastScanTime > SCAN_COOLDOWN) {
                            handleScanResult(result);
                            lastScanTime = now;
                        }
                    }
                } catch (err) {
                    // Игнорируем ошибки NotFoundException
                    if (!err.message.includes('NotFoundException')) {
                        console.error(err);
                    }
                } finally {
                    isProcessing = false;
                    if (scannerActive) {
                        setTimeout(startScanner, 100); // Задержка между кадрами
                    }
                }
            });
        }
        
        function handleScanResult(result) {
            if (beepSound) {
                beepSound.currentTime = 0;
                beepSound.play().catch(e => console.log("Не удалось воспроизвести звук:", e));
            }
            
            barcodeInput.value = result.text;
            
            // Убрана автоматическая фокусировка на поле имени
            fetch(`/get-product-name?barcode=${result.text}`)
                .then(res => res.json())
                .then(data => {
                    if (data.found) {
                        document.getElementById('name').value = data.name;
                    }
                });
        }
        
        // Исправленная отправка формы
        scannerForm.addEventListener('submit', (e) => {
            const requiredFields = scannerForm.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'red';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert("Пожалуйста, заполните все обязательные поля");
            }
        });
        
        // Инициализация
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            startCamera();
        } else {
            showCameraError();
            cameraError.textContent = "Ваш браузер не поддерживает доступ к камере";
            barcodeInput.removeAttribute('readonly');
            barcodeInput.placeholder = "Введите штрих-код вручную";
        }

        // Остальные обработчики без изменений
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
