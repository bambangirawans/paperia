from datetime import datetime
from .. import db


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    corrected_text = db.Column(db.Text, nullable=True)
    labeled_text = db.Column(db.Text, nullable=True)
    manual_corrected_text = db.Column(db.Text, nullable=True)
    doc_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
    def __repr__(self):
        return f'<Document {self.filename}>'

    @staticmethod
    def get_documents(start_date=None, end_date=None, doc_type=None, manual_corrected_only=True):
        query = Document.query
        if start_date:
            query = query.filter(Document.created_at >= start_date)
        if end_date:
            query = query.filter(Document.created_at <= end_date)
        if doc_type:
            query = query.filter(Document.doc_type == doc_type)
        if manual_corrected_only:
            query = query.filter(Document.manual_corrected_text != None)  
        return query.all()
        
        
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    zip = db.Column(db.String(7))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    zip = db.Column(db.String(7))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    zip = db.Column(db.String(7))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    unit_price = db.Column(db.Numeric(10, 2))
    unit = db.Column(db.String(100))
    unit_sale = db.Column(db.String(100))
    selling_price = db.Column(db.Numeric(10, 2))
    purchase_price = db.Column(db.Numeric(10, 2))
    stock_onhand = db.Column(db.Integer)
    stock_reorder = db.Column(db.Integer)
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    image = db.Column(db.String(255))
    imagepath = db.Column(db.String(255))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    subtotal = db.Column(db.Numeric(10, 2))
    discount = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    tax = db.Column(db.Numeric(10, 2))
    amount = db.Column(db.Numeric(10, 2))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    qty = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(10, 2))
    unit_sale = db.Column(db.String(100))
    subtotal = db.Column(db.Numeric(10, 2))
    discount = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    tax = db.Column(db.Numeric(10, 2))
    amount = db.Column(db.Numeric(10, 2))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    subtotal = db.Column(db.Numeric(10, 2))
    discount = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    tax = db.Column(db.Numeric(10, 2))
    amount = db.Column(db.Numeric(10, 2))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    qty = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(10, 2))
    unit_sale = db.Column(db.String(100))
    subtotal = db.Column(db.Numeric(10, 2))
    discount = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    tax = db.Column(db.Numeric(10, 2))
    amount = db.Column(db.Numeric(10, 2))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

class Issuer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(50))  # cash, bank, fintech
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    zip = db.Column(db.String(7))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(50))  # saving, giro, e-wallet, petty cash, etc.
    issuer_id = db.Column(db.Integer, db.ForeignKey('issuer.id'))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

class AccountTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    type = db.Column(db.String(100))  # customer receipt, supplier payment, other receipt, other payment, deposit, withdrawal, refund
    description = db.Column(db.String(255))
    reff = db.Column(db.String(255))
    amount = db.Column(db.Numeric(10, 2))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    debt_credit = db.Column(db.String(1))
    created = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))