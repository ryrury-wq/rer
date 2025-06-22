from flask import render_template_stringMore actions

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
            position: relative;
        }
        .logo {
            font-weight: 700;
            font-size: 1.8em;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
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
        .container {
            max-width: 100%;
            padding: 15px;
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
        .edit-btn, .delete-btn {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            cursor: pointer;
            border: none;
        }
    
        .edit-btn {
            background: #ffc107;
            color: #333;
        }
    
        .delete-btn {
            background: #f44336;
            color: white;
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
            transition: all 0.2s;
            text-align: center;
            flex: 1;
            min-width: calc(50% - 10px);
            box-sizing: border-box;
        }
        .nav-links .full-width {
            flex: 0 0 100%;
            min-width: 100%;
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
        .no-items {
            text-align: center;
            padding: 30px;
            color: #9e9e9e;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="back-btn">←</a>
        <h1 class="logo">Вкусвилл</h1>
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
            <a href="/assortment" class="full-width">Ассортимент</a>
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
                    <div style="display: flex; gap: 5px;">
                         <form action="/move_to_history" method="POST" style="display: inline;">
                           <input type="hidden" name="batch_id" value="{{ item.id }}">
                           <button type="submit" class="move-btn" title="Переместить в историю">→</button>
                         </form>
        
                         <a href="/edit_batch/{{ item.id }}" class="edit-btn" title="Редактировать">✎</a>
        
                         <form action="/delete_batch/{{ item.id }}" method="POST" style="display: inline;">
                           <button type="submit" class="delete-btn" title="Удалить">✕</button>
                         </form>
                    </div>
                    
                    <form action="/move_to_history" method="POST" style="display: inline;">
                        <input type="hidden" name="batch_id" value="{{ item.id }}">
                        <button type="submit" class="move-btn" title="Переместить в историю">→</button>
                    </form>
                </div>
            {% else %}
                <div class="no-items">
                    Нет товаров с истекающим сроком
                </div>
            {% endfor %}
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
                
                const items = itemsContainer.querySelectorAll('.item');
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
                    itemsContainer.innerHTML = `<div class="no-items">
                        Ничего не найдено по запросу: "${searchTerm}"
                    </div>`;
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
        .tabs {
            display: flex;
            margin: 20px 0 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            font-weight: 500;
            color: #757575;
        }
        .tab.active {
            border-bottom: 3px solid #00a046;
            color: #00a046;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .calculated-expiry {
            padding: 12px;
            background: #e8f5e9;
            border-radius: 8px;
            margin-top: 10px;
            text-align: center;
            font-weight: 500;
            color: #2e7d32;
        }
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
                
                <div class="tabs">
                    <div class="tab active" data-tab="by-date">По дате изготовления</div>
                    <div class="tab" data-tab="by-expiry">По сроку годности</div>
                </div>
                
                <div class="tab-content active" id="by-date">
                    <div class="form-group">
                        <label for="manufacture_date_text">Дата изготовления (дд.мм.гггг):</label>
                        <div class="date-input-group">
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
                    
                    <div id="calculated-expiry" class="calculated-expiry">
                        Рассчитанный срок годности: <span id="expiry-result">-</span>
                    </div>
                </div>
                
                <div class="tab-content" id="by-expiry">
                    <div class="form-group">
                        <label for="expiration_date_text">Срок годности (дд.мм.гггг):</label>
                        <div class="date-input-group">
                            <input type="date" name="expiration_date" id="expiration_date" style="display: none">
                            <input type="text" id="expiration_date_text" placeholder="дд.мм.гггг" required>
                        </div>
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
        // Элементы для работы с датами
        const dateFields = {
            'manufacture': {
                text: document.getElementById('manufacture_date_text'),
                hidden: document.getElementById('manufacture_date'),
                error: null
            },
            'expiration': {
                text: document.getElementById('expiration_date_text'),
                hidden: document.getElementById('expiration_date'),
                error: null
            }
        };
        
        // Функция для инициализации работы с датами
        function setupDateInput(type) {
            const {text, hidden} = dateFields[type];
            
            text.addEventListener('input', function(e) {
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
                        hidden.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                    }
                }
                
                // Обновляем расчет срока годности
                if (type === 'manufacture') {
                    calculateExpiry();
                }
            });
                
            text.addEventListener('blur', function() {
                const value = text.value;
                if (value.length > 0 && value.length < 10) {
                    alert('Пожалуйста, введите полную дату в формате дд.мм.гггг');
                    text.focus();
                } else if (value.length === 10) {
                    const parts = value.split('.');
                    if (parts.length === 3) {
                        const [day, month, year] = parts;
                        hidden.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                    }
                }
            });
                
            text.addEventListener('keydown', function(e) {
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
        
        // Инициализация полей дат
        setupDateInput('manufacture');
        setupDateInput('expiration');
        
        // Обработка вкладок
        const tabs = document.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                this.classList.add('active');
                
                const tabId = this.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
            });
        });
        
        // Функция для расчета срока годности
        function calculateExpiry() {
            const mDate = document.getElementById('manufacture_date').value;
            const durationValue = document.querySelector('input[name="duration_value"]').value;
            const durationUnit = document.querySelector('select[name="duration_unit"]').value;
            const expiryResult = document.getElementById('expiry-result');
            
            if (mDate && durationValue && durationUnit) {
                const mDateObj = new Date(mDate);
                let expiryDate = new Date(mDateObj);
                
                if (durationUnit === 'days') {
                    expiryDate.setDate(expiryDate.getDate() + parseInt(durationValue));
                } else if (durationUnit === 'months') {
                    expiryDate.setMonth(expiryDate.getMonth() + parseInt(durationValue));
                } else if (durationUnit === 'years') {
                    expiryDate.setFullYear(expiryDate.getFullYear() + parseInt(durationValue));
                }
                
                // Форматируем дату в дд.мм.гггг
                const day = String(expiryDate.getDate()).padStart(2, '0');
                const month = String(expiryDate.getMonth() + 1).padStart(2, '0');
                const year = expiryDate.getFullYear();
                
                expiryResult.textContent = `${day}.${month}.${year}`;
            } else {
                expiryResult.textContent = '-';
            }
        }
        
        // Слушатели для расчета срока годности
        document.getElementById('manufacture_date_text').addEventListener('input', calculateExpiry);
        document.querySelector('input[name="duration_value"]').addEventListener('input', calculateExpiry);
        document.querySelector('select[name="duration_unit"]').addEventListener('change', calculateExpiry);
        
        // Инициализация расчета
        calculateExpiry();
        
        // Проверка дат перед отправкой
        scannerForm.addEventListener('submit', function(e) {
            const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');
            
            if (activeTab === 'by-date') {
                const manufactureDate = document.getElementById('manufacture_date').value;
                if (!manufactureDate || manufactureDate.length !== 10) {
                    e.preventDefault();
                    alert('Пожалуйста, введите корректную дату изготовления в формате дд.мм.гггг');
                    document.getElementById('manufacture_date_text').focus();
                    return;
                }
            } else if (activeTab === 'by-expiry') {
                const expirationDate = document.getElementById('expiration_date').value;
                if (!expirationDate || expirationDate.length !== 10) {
                    e.preventDefault();
                    alert('Пожалуйста, введите корректную дату срока годности в формате дд.мм.гггг');
                    document.getElementById('expiration_date_text').focus();
                    return;
                }
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
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
        }
        .tab.active {
            border-bottom: 3px solid #00a046;
            color: #00a046;
            font-weight: 500;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
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
            
            <div class="tabs">
                <div class="tab active" data-tab="by-date">По дате изготовления</div>
                <div class="tab" data-tab="by-expiry">По сроку годности</div>
            </div>
            
            <form method="POST" id="add-batch-form">
                <div class="tab-content active" id="by-date">
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
                            <input type="number" name="duration_value" placeholder="Количество" required min="1">
                            <select name="duration_unit" required>
                                <option value="days">дней</option>
                                <option value="months">месяцев</option>
                                <option value="years">лет</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="tab-content" id="by-expiry">
                    <div class="form-group">
                        <label>Срок годности (дд.мм.гггг):</label>
                        <div class="date-input-group">
                            <span class="date-icon">📅</span>
                            <input type="hidden" id="expiration_date" name="expiration_date">
                            <input type="text" id="expiration_date_text" class="date-input" placeholder="дд.мм.гггг" required>
                            <div class="error-message" id="expiration_date_error">Пожалуйста, введите дату в формате дд.мм.гггг</div>
                        </div>
                    </div>
                </div>
                
                <button type="submit">Добавить срок</button>
            </form>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tabs = document.querySelectorAll('.tab');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    tabs.forEach(t => t.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));
                    
                    this.classList.add('active');
                    
                    const tabId = this.getAttribute('data-tab');
                    document.getElementById(tabId).classList.add('active');
                });
            });
            
            // Функции для обработки ввода даты
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
            
            // Настройка полей для дат
            setupDateInput('manufacture_date_text', 'manufacture_date', 'manufacture_date_error');
            setupDateInput('expiration_date_text', 'expiration_date', 'expiration_date_error');
            
            // Обработка отправки формы
            document.getElementById('add-batch-form').addEventListener('submit', function(e) {
                let isValid = true;
                const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');
                
                if (activeTab === 'by-date') {
                    const manufactureDate = document.getElementById('manufacture_date').value;
                    if (!manufactureDate || manufactureDate.length !== 10) {
                        document.getElementById('manufacture_date_error').style.display = 'block';
                        isValid = false;
                    }
                } else if (activeTab === 'by-expiry') {
                    const expirationDate = document.getElementById('expiration_date').value;
                    if (!expirationDate || expirationDate.length !== 10) {
                        document.getElementById('expiration_date_error').style.display = 'block';
                        isValid = false;
                    }
                }
                
                if (!isValid) {
                    e.preventDefault();
                    alert('Пожалуйста, введите корректные даты в формате дд.мм.гггг');
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
        }
        .product-item:hover {
            background: #f5f5f5;
            transform: translateY(-2px);
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .item-info { 
            flex-grow: 1;
            padding-right: 15px;
        }
        .add-btn {
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
            font-size: 24px;
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
        .empty-assortment {
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
        .batch-count {
            display: inline-block;
            padding: 2px 8px;
            background: #e0f7fa;
            border-radius: 12px;
            font-size: 0.8em;
            margin-top: 5px;
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
                        <a href="/add_batch?barcode={{ product['barcode'] }}" class="add-btn" title="Добавить срок годности">+</a>
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
            padding: 30px 15px 10px;
            color: #757575;
            font-size: 0.85em;
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
            <h1>Редактирование товара</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Наименование:</label>
                    <input type="text" name="name" value="{{ item.name }}" required>
                </div>
                <div class="form-group">
                    <label>Штрих-код:</label>
                    <input type="text" name="barcode" value="{{ item.barcode }}" required>
                </div>
                <div class="form-group">
                    <label>Срок годности (дд.мм.гггг):</label>
                    <input type="date" name="expiration_date" id="expiration_date" style="display: none">
                    <input type="text" id="expiration_date_text" value="{{ item.expiration_date }}" required>
                </div>
                <button type="submit">Сохранить изменения</button>
            </form>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const dateField = document.getElementById('expiration_date');
            const textField = document.getElementById('expiration_date_text');
            
            // Преобразуем дату из формата YYYY-MM-DD в дд.мм.гггг для отображения
            const parts = textField.value.split('-');
            if (parts.length === 3) {
                const [year, month, day] = parts;
                textField.value = `${day}.${month}.${year}`;
            }
            
            // Обработка ввода
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
                    }
                }
            });
        });
    </script>
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
    'history.html': history_html
    'history.html': history_html,
    'edit_batch.html': edit_batch_html 
}

def render_template(template_name, **context):
    """Кастомная функция рендеринга шаблонов"""
    return render_template_string(templates[template_name], **context)
