from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Requester, Approver, Purchasing, Warehouse, Admin
    department = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requested_prs = db.relationship('PurchaseRequisition', foreign_keys='PurchaseRequisition.requester_id', backref='requester', lazy=True)
    approved_prs = db.relationship('PurchaseRequisition', foreign_keys='PurchaseRequisition.approver_id', backref='approver', lazy=True)
    created_pos = db.relationship('PurchaseOrder', backref='purchasing_officer', lazy=True)
    received_grs = db.relationship('GoodsReceipt', backref='warehouse_officer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class PurchaseRequisition(db.Model):
    __tablename__ = 'purchase_requisitions'

    id = db.Column(db.Integer, primary_key=True)
    pr_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    request_date = db.Column(db.Date, default=date.today, nullable=False)
    required_date = db.Column(db.Date, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    total_estimated_amount = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Approved, Rejected, PO Created
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('PRItem', backref='pr', cascade='all, delete-orphan', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='pr', lazy=True)

    def calculate_total(self):
        self.total_estimated_amount = sum(item.subtotal for item in self.items)
        return self.total_estimated_amount

    def __repr__(self):
        return f'<PR {self.pr_number} - {self.status}>'


class PRItem(db.Model):
    __tablename__ = 'pr_items'

    id = db.Column(db.Integer, primary_key=True)
    pr_id = db.Column(db.Integer, db.ForeignKey('purchase_requisitions.id', ondelete='CASCADE'), nullable=False)
    item_name = db.Column(db.String(150), nullable=False)
    specification = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit = db.Column(db.String(20), nullable=False, default='Pcs')
    estimated_price = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

    def calculate_subtotal(self):
        self.subtotal = float(self.quantity or 0) * float(self.estimated_price or 0.0)
        return self.subtotal

    def __repr__(self):
        return f'<PRItem {self.item_name} ({self.quantity} {self.unit})>'


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    pr_id = db.Column(db.Integer, db.ForeignKey('purchase_requisitions.id', ondelete='RESTRICT'), nullable=False)
    purchasing_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    vendor_name = db.Column(db.String(150), nullable=False)
    vendor_address = db.Column(db.Text, nullable=True)
    vendor_phone = db.Column(db.String(30), nullable=True)
    vendor_email = db.Column(db.String(100), nullable=True)
    po_date = db.Column(db.Date, default=date.today, nullable=False)
    delivery_estimate_date = db.Column(db.Date, nullable=True)
    payment_terms = db.Column(db.String(50), default='Net 30')
    notes = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(25), default='Issued', nullable=False)  # Issued, Partially Received, Received, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('POItem', backref='po', cascade='all, delete-orphan', lazy=True)
    goods_receipts = db.relationship('GoodsReceipt', backref='po', lazy=True)

    def calculate_total(self):
        self.total_amount = sum(item.subtotal for item in self.items)
        return self.total_amount

    def update_receipt_status(self):
        """Mengecek apakah seluruh item PO telah diterima lengkap"""
        total_ordered = sum(item.quantity for item in self.items)
        total_received = 0
        for gr in self.goods_receipts:
            for gi in gr.items:
                total_received += gi.quantity_received
        
        if total_received >= total_ordered and total_ordered > 0:
            self.status = 'Received'
        elif total_received > 0:
            self.status = 'Partially Received'
        else:
            self.status = 'Issued'

    def __repr__(self):
        return f'<PO {self.po_number} - {self.vendor_name}>'


class POItem(db.Model):
    __tablename__ = 'po_items'

    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id', ondelete='CASCADE'), nullable=False)
    pr_item_id = db.Column(db.Integer, db.ForeignKey('pr_items.id', ondelete='SET NULL'), nullable=True)
    item_name = db.Column(db.String(150), nullable=False)
    specification = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='Pcs')
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    # Relationship to PRItem
    pr_item = db.relationship('PRItem', backref='po_items', lazy=True)

    def __repr__(self):
        return f'<POItem {self.item_name} ({self.quantity} {self.unit})>'


class GoodsReceipt(db.Model):
    __tablename__ = 'goods_receipts'

    id = db.Column(db.Integer, primary_key=True)
    gr_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id', ondelete='RESTRICT'), nullable=False)
    warehouse_officer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    delivery_order_number = db.Column(db.String(50), nullable=False)  # Nomor Surat Jalan Vendor
    received_date = db.Column(db.Date, default=date.today, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(25), default='Complete', nullable=False)  # Partial, Complete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('GRItem', backref='goods_receipt', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<GR {self.gr_number} (DO: {self.delivery_order_number})>'


class GRItem(db.Model):
    __tablename__ = 'gr_items'

    id = db.Column(db.Integer, primary_key=True)
    gr_id = db.Column(db.Integer, db.ForeignKey('goods_receipts.id', ondelete='CASCADE'), nullable=False)
    po_item_id = db.Column(db.Integer, db.ForeignKey('po_items.id', ondelete='RESTRICT'), nullable=False)
    quantity_received = db.Column(db.Integer, nullable=False)
    condition_status = db.Column(db.String(50), default='Baik', nullable=False)  # Baik, Rusak, Tidak Sesuai
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    po_item = db.relationship('POItem', backref='gr_items', lazy=True)

    def __repr__(self):
        return f'<GRItem PO-Item:{self.po_item_id} Qty:{self.quantity_received} [{self.condition_status}]>'
