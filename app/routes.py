import os
import logging
import openai

from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime 
from .models.db import db, Document, Organization, Customer, Supplier, Product, ProductImage, Invoice, InvoiceItem, Purchase, PurchaseItem, Issuer, Account, AccountTransaction
from .models.ocr import scan_and_detect, extract_text_from_image, correct_text, preprocess_image
from .models.payment import process_payment
from .models.customer_service import generate_response
from .models.goods_receipt import verify_goods_receipt
from .models.sales_and_marketing import process_sales_and_marketing

main_bp = Blueprint('main', __name__)

# Configure the upload folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','pdf'}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload and scan items
@main_bp.route('/scan_item', methods=['POST'])
def scan_item():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        image_path = os.path.join(upload_folder, filename)
        file.save(image_path)
        
        # Perform object detection and OCR
        detected_items = scan_and_detect(image_path)
        
        return jsonify(detected_items), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

def parse_invoice(text):
    invoice_data = {}
    invoice_data['invoice_number'] = re.search(r'Invoice Number:\s*(\S+)', text).group(1)
    invoice_data['date'] = re.search(r'Date:\s*([\d-]+)', text).group(1)
    invoice_data['subtotal'] = re.search(r'Subtotal:\s*\$?([\d.]+)', text).group(1)
    invoice_data['total'] = re.search(r'Total:\s*\$?([\d.]+)', text).group(1)
    return invoice_data

def parse_customer(text):
    customer_data = {}
    customer_data['name'] = re.search(r'Customer Name:\s*(.+)', text).group(1)
    customer_data['address'] = re.search(r'Address:\s*(.+)', text).group(1)
    customer_data['phone'] = re.search(r'Phone:\s*(\S+)', text).group(1)
    return customer_data

def parse_products(text):
    products = []
    product_pattern = re.compile(r'Product:\s*(.+?)\s*Qty:\s*(\d+)\s*Price:\s*\$?([\d.]+)', re.DOTALL)
    for match in product_pattern.finditer(text):
        product_data = {
            'name': match.group(1).strip(),
            'quantity': int(match.group(2)),
            'unit_price': float(match.group(3))
        }
        products.append(product_data)
    return products

    
def save_invoice_data(text):
    invoice_data = parse_invoice(text)
    customer_data = parse_customer(text)
    products_data = parse_products(text)
    
    customer = Customer.query.filter_by(name=customer_data['name']).first()
    if not customer:
        customer = Customer(
            name=customer_data['name'],
            address=customer_data['address'],
            phone=customer_data['phone']
        )
        db.session.add(customer)
        db.session.commit()
    
    invoice = Invoice(
        date=datetime.strptime(invoice_data['date'], '%Y-%m-%d'),
        customer_id=customer.id,
        subtotal=float(invoice_data['subtotal']),
        total=float(invoice_data['total'])
    )
    db.session.add(invoice)
    db.session.commit()
    
    for product_data in products_data:
        product = Product.query.filter_by(name=product_data['name']).first()
        if not product:
            product = Product(
                name=product_data['name'],
                unit_price=product_data['unit_price']
            )
            db.session.add(product)
            db.session.commit()
        
        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=product.id,
            qty=product_data['quantity'],
            unit_price=product.unit_price,
            total=product_data['quantity'] * product.unit_price
        )
        db.session.add(invoice_item)
    
    db.session.commit()
    
    return 'invoice successfully processed'


@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'document' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['document']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            # Ensure the upload folder exists
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, secure_filename(file.filename))
            file.save(file_path)

            # Log the file path
            logging.info(f'File saved at: {file_path}')
            #preprocessed_image_path = preprocess_image(file_path)
            extracted_text = extract_text_from_image(file_path)
            #extracted_text =extract_text_with_deep_learning(file_path)
            doc_type = request.form.get('doc_type')
            corrected_text, labeled_text = correct_text(extracted_text)

            new_document = Document(
                filename=file.filename, 
                text=extracted_text, 
                corrected_text=corrected_text,
                labeled_text=labeled_text,
                doc_type=doc_type,
                manual_corrected_text=''
            )
            db.session.add(new_document)
            db.session.commit()
            return redirect(url_for('main.edit', doc_id=new_document.id))
            
    return render_template('upload.html')

@main_bp.route('/edit/<doc_id>', methods=['GET', 'POST'])
def edit(doc_id):
    document = Document.query.get(doc_id)
    if request.method == 'POST':
        updated_text = request.form['documentText']
        document.manual_corrected_text = updated_text
        db.session.commit()
        
        
        data = parse_invoice(updated_text)
        save_invoice_data(data)
            
        ''' 
        doc_type =document.doc_type
        
        if doc_type == 'invoice':
            data = parse_invoice(updated_text)
            save_invoice_data(data)
        elif doc_type == 'purchase':
            data = parse_purchase(updated_text)
            save_purchase_data(data)
        elif doc_type == 'supplier_payment':
            data = parse_supplier_payment(updated_text)
            save_supplier_payment_data(data)
        elif doc_type == 'customer_receipt':
            data = parse_customer_receipt(updated_text)
            save_customer_receipt_data(data)
        elif doc_type == 'other_payment':
            data = parse_other_payment(updated_text)
            save_other_payment_data(data)
        elif doc_type == 'other_receipt':
            data = parse_other_receipt(updated_text)
            save_other_receipt_data(data)
        else:
            data = parse_other_document(updated_text)
            save_other_document_data(data)
        '''
        
        return redirect(url_for('main.dashboard'))

    return render_template('edit.html', doc_id=doc_id, doc_text=document.manual_corrected_text or document.corrected_text)


@main_bp.before_app_request
def create_tables():
    db.create_all()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route to upload multiple images for batch processing (optional)
@main_bp.route('/batch_scan', methods=['POST'])
def batch_scan():
    files = request.files.getlist('images')
    results = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(image_path)
            
            detected_items = scan_and_detect(image_path)
            results.append({filename: detected_items})

    return jsonify(results), 200

@main_bp.route('/payment', methods=['POST'])
def payment():
    data = request.get_json()
    payment_result = process_payment(data)
    return jsonify(payment_result), 200

@main_bp.route('/customer_service', methods=['POST'])
def customer_service():
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400

    response = generate_response(user_message)
    return jsonify(response), 200

@main_bp.route('/receive_goods', methods=['POST'])
def receive_goods():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image = request.files['image']
    expected_items = request.form.get('expected_items')

    if not expected_items:
        return jsonify({'status': 'error', 'message': 'No expected items provided'}), 400

    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    expected_items = json.loads(expected_items)  # Ensure expected_items is in correct format

    response = process_goods_receipt(image_path, expected_items)
    return jsonify(response), 200
    
def generate_analysis(summary):
    openai.api_key = current_app.config['OPENAI_API_KEY']
    
    prompt = f"Generate a business analysis and recommendations based on the following data: {summary}"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    
    return response.choices[0].text.strip()
    
@main_bp.route('/sales_report', methods=['GET', 'POST'])
def sales_report():
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        # Check if dates are provided
        if not start_date_str or not end_date_str:
            start_date = datetime.min  # Default start date (earliest possible)
            end_date = datetime.max    # Default end date (latest possible)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError as e:
                return f"Error parsing dates: {e}"

        # Fetch data from the database
        if start_date and end_date:
            invoices = db.session.query(Invoice).filter(Invoice.date.between(start_date, end_date)).all()
            invoice_items = db.session.query(InvoiceItem).join(Invoice).filter(Invoice.date.between(start_date, end_date)).all()
        else:
            invoices = db.session.query(Invoice).all()
            invoice_items = db.session.query(InvoiceItem).all()

        customers = db.session.query(Customer).all()
        products = db.session.query(Product).all()

        # Process data to create a summary (this can be more complex depending on your requirements)
        summary = {
            'total_invoices': len(invoices),
            'total_revenue': sum(item.price * item.quantity for item in invoice_items),
            'total_customers': len(customers),
            'total_products_sold': sum(item.quantity for item in invoice_items),
        }

        generate_analysis(summary)

        return render_template('sales_report_result.html', summary=summary, analysis=analysis)

    # Render the form initially
    return render_template('sales_report.html')

