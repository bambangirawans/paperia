import os
import logging

from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app, jsonify
from werkzeug.utils import secure_filename

from .models.db import db, Document, Organization, Customer, Supplier, Product, ProductImage, Invoice, InvoiceItem, Purchase, PurchaseItem, Issuer, Account, AccountTransaction
from .models.ocr import scan_and_detect, extract_text_from_image, correct_text, preprocess_image
from .models.payment import process_payment
from .models.customer_service import generate_response
from .models.goods_receipt import verify_goods_receipt
from .models.sales_and_marketing import process_sales_and_marketing

main_bp = Blueprint('main', __name__)

# Configure the upload folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

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



# Sales and marketing route
@main_bp.route('/sales_and_marketing', methods=['POST'])
def sales_and_marketing():
    data = request.get_json()
    customers_df = pd.DataFrame(data)  # Assuming the data is in a DataFrame format

    response = process_sales_and_marketing(customers_df)
    return jsonify(response), 200