import os
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, jsonify
from supabase import create_client

app = Flask(__name__)

# Инициализация Supabase
supabase_url = os.environ.get("https://pjohxnvnfbfyjouspczz.supabase.co")
supabase_key = os.environ.get("123Rus#")
supabase = create_client(supabase_url, supabase_key)

# Очистка старых записей истории
def clear_old_history():
    three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    supabase.table("history").delete().lt("removed_date", three_months_ago).execute()

# Удаление товаров через месяц после истечения срока
def remove_expired():
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)
    
    # Получаем просроченные товары
    expired = supabase.table("batches").select("id, products(barcode, name), expiration_date").lte("expiration_date", one_month_ago).execute().data
    
    for item in expired:
        # Проверяем наличие в истории
        history_check = supabase.table("history").select("*").eq("barcode", item["products"]["barcode"]).eq("expiration_date", item["expiration_date"]).execute()
        
        if not history_check.data:
            # Добавляем в историю
            supabase.table("history").insert({
                "barcode": item["products"]["barcode"],
                "product_name": item["products"]["name"],
                "expiration_date": item["expiration_date"],
                "removed_date": today.strftime('%Y-%m-%d')
            }).execute()
        
        # Удаляем из активных
        supabase.table("batches").delete().eq("id", item["id"]).execute()

@app.route('/')
def index():
    today = datetime.now().date()
    
    # Получаем все активные товары
    items_data = supabase.table("batches").select("id, expiration_date, added_date, products(name, barcode)").order("expiration_date").execute().data
    
    items = []
    for row in items_data:
        exp_date = datetime.strptime(row['expiration_date'], "%Y-%m-%d").date()
        days_until_expiry = (exp_date - today).days
        
        days_since_expiry = max(0, (today - exp_date).days)
        removal_date = exp_date + timedelta(days=30)
        days_until_removal = max(0, (removal_date - today).days)
        
        status = "normal"
        if days_since_expiry > 0:
            status = "expired"
        elif days_until_expiry == 0:
            status = "expired"
        elif days_until_expiry == 1:
            status = "warning"
        elif days_until_expiry <= 7:
            status = "soon"
        
        items.append({
            'id': row['id'],
            'name': row['products']['name'],
            'barcode': row['products']['barcode'],
            'expiration_date': row['expiration_date'],
            'days_since_expiry': days_since_expiry,
            'days_until_removal': days_until_removal,
            'removal_date': removal_date.strftime('%Y-%m-%d'),
            'days_until_expiry': days_until_expiry,
            'status': status
        })
    
    return render_template('index.html', items=items)

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        barcode = request.form['barcode']
        name = request.form['name']
        manufacture_date = request.form['manufacture_date']
        duration_value = int(request.form['duration_value'])
        duration_unit = request.form['duration_unit']
        
        # Рассчет срока годности
        m_date = datetime.strptime(manufacture_date, '%Y-%m-%d')
        if duration_unit == 'days':
            exp_date = m_date + timedelta(days=duration_value)
        elif duration_unit == 'months':
            exp_date = m_date + timedelta(days=duration_value*30)
        elif duration_unit == 'hours':
            exp_date = m_date + timedelta(hours=duration_value)
        else:
            exp_date = m_date + timedelta(days=30)
        
        exp_date_str = exp_date.strftime('%Y-%m-%d')
        
        # Проверка существования товара
        product_check = supabase.table("products").select("id").eq("barcode", barcode).execute()
        
        if not product_check.data:
            # Создаем новый продукт
            new_product = supabase.table("products").insert({
                "barcode": barcode,
                "name": name
            }).execute().data[0]
            product_id = new_product["id"]
        else:
            product_id = product_check.data[0]["id"]
        
        # Добавляем партию
        supabase.table("batches").insert({
            "product_id": product_id,
            "expiration_date": exp_date_str
        }).execute()
        
        return redirect(url_for('index'))
        
    return render_template('scan.html')

@app.route('/get-product-name', methods=['GET'])
def get_product_name():
    barcode = request.args.get('barcode')
    product = supabase.table("products").select("name").eq("barcode", barcode).execute().data
    if product:
        return jsonify({'found': True, 'name': product[0]['name']})
    else:
        return jsonify({'found': False})

@app.route('/get-all-products', methods=['GET'])
def get_all_products():
    products = supabase.table("products").select("barcode, name").execute().data
    return jsonify({'products': products})

@app.route('/new_product', methods=['GET', 'POST'])
def new_product():
    barcode = request.args.get('barcode')
    if request.method == 'POST':
        name = request.form['name']
        barcode = request.form['barcode']
        supabase.table("products").insert({
            "barcode": barcode,
            "name": name
        }).execute()
        return redirect(url_for('add_batch', barcode=barcode))
    return render_template('new_product.html', barcode=barcode)

@app.route('/add_batch', methods=['GET', 'POST'])
def add_batch():
    barcode = request.args.get('barcode')
    product = supabase.table("products").select("id, name").eq("barcode", barcode).execute().data
    
    if not product:
        return "Товар не найден", 404
    
    product = product[0]

    if request.method == 'POST':
        expiration_date = request.form['expiration_date']
        supabase.table("batches").insert({
            "product_id": product["id"],
            "expiration_date": expiration_date
        }).execute()
        return redirect(url_for('index'))

    return render_template('add_batch.html', product_name=product["name"])

@app.route('/history')
def history():
    history_items = supabase.table("history").select("*").order("removed_date", desc=True).execute().data
    return render_template('history.html', history_items=history_items)

@app.route('/move_to_history', methods=['POST'])
def move_to_history():
    batch_id = request.form['batch_id']
    today = datetime.now().date().strftime('%Y-%m-%d')
    
    # Получаем информацию о товаре
    batch_info = supabase.table("batches").select("products(barcode, name), expiration_date").eq("id", batch_id).execute().data
    
    if batch_info:
        batch_info = batch_info[0]
        # Проверяем наличие в истории
        history_check = supabase.table("history").select("id").eq("barcode", batch_info["products"]["barcode"]).eq("expiration_date", batch_info["expiration_date"]).execute()
        
        if not history_check.data:
            # Добавляем в историю
            supabase.table("history").insert({
                "barcode": batch_info["products"]["barcode"],
                "product_name": batch_info["products"]["name"],
                "expiration_date": batch_info["expiration_date"],
                "removed_date": today
            }).execute()
        
        # Удаляем из активных
        supabase.table("batches").delete().eq("id", batch_id).execute()
    
    return redirect(url_for('index'))

@app.route('/restore_from_history', methods=['POST'])
def restore_from_history():
    history_id = request.form['history_id']
    # Получаем информацию из истории
    history_item = supabase.table("history").select("*").eq("id", history_id).execute().data
    
    if history_item:
        history_item = history_item[0]
        # Проверяем существование товара
        product_check = supabase.table("products").select("id").eq("barcode", history_item["barcode"]).execute()
        
        if not product_check.data:
            # Создаем новый товар
            new_product = supabase.table("products").insert({
                "barcode": history_item["barcode"],
                "name": history_item["product_name"]
            }).execute().data[0]
            product_id = new_product["id"]
        else:
            product_id = product_check.data[0]["id"]
        
        # Добавляем обратно в активные
        supabase.table("batches").insert({
            "product_id": product_id,
            "expiration_date": history_item["expiration_date"]
        }).execute()
        
        # Удаляем из истории
        supabase.table("history").delete().eq("id", history_id).execute()
    
    return redirect(url_for('history'))

def run_app():
    remove_expired()
    clear_old_history()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# Импорт шаблонов после объявления app
from templates import render_template

if __name__ == '__main__':
    run_app()
