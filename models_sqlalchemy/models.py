
from . import db, TimestampMixin
import random
import string

class ProviderProfile(db.Model, TimestampMixin):
    """Provider business profile"""
    __tablename__ = 'provider_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    business_name = db.Column(db.String(200), nullable=False)
    business_description = db.Column(db.Text)
    business_address = db.Column(db.String(255))
    tax_id = db.Column(db.String(50))
    is_approved = db.Column(db.Boolean, default=False)
    
    # Relationships
    products = db.relationship('Product',
        primaryjoin='ProviderProfile.user_id == Product.provider_id',
        foreign_keys='Product.provider_id',
        backref='provider_profile', lazy='dynamic', viewonly=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'business_description': self.business_description,
            'business_address': self.business_address,
            'tax_id': self.tax_id,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(db.Model, TimestampMixin):
    """Product model"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    wattage = db.Column(db.Integer)
    battery_capacity = db.Column(db.String(50))
    solar_panel_type = db.Column(db.String(100))
    lighting_duration = db.Column(db.String(50))
    warranty_period = db.Column(db.String(50))
    stock_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'wattage': self.wattage,
            'battery_capacity': self.battery_capacity,
            'solar_panel_type': self.solar_panel_type,
            'lighting_duration': self.lighting_duration,
            'warranty_period': self.warranty_period,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model, TimestampMixin):
    """Order model"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    order_status = db.Column(db.String(20), default='pending')
    shipping_address = db.Column(db.Text)
    phone_number = db.Column(db.String(20))
    
    # M-PESA specific fields
    mpesa_checkout_request_id = db.Column(db.String(100))
    mpesa_merchant_request_id = db.Column(db.String(100))
    mpesa_receipt_number = db.Column(db.String(100))
    mpesa_transaction_date = db.Column(db.DateTime)
    mpesa_phone_number = db.Column(db.String(20))
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    support_tickets = db.relationship('SupportTicket', backref='order', lazy='dynamic')
    
    @staticmethod
    def generate_order_number():
        return 'ORD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'order_number': self.order_number,
            'total_amount': float(self.total_amount),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'order_status': self.order_status,
            'shipping_address': self.shipping_address,
            'phone_number': self.phone_number,
            'mpesa_checkout_request_id': self.mpesa_checkout_request_id,
            'mpesa_receipt_number': self.mpesa_receipt_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OrderItem(db.Model, TimestampMixin):
    """Order item model"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': float(self.price),
            'product_name': self.product.name if self.product else None,
            'image_url': self.product.image_url if self.product else None
        }

class CartItem(db.Model, TimestampMixin):
    """Shopping cart item"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'name': self.product.name if self.product else None,
            'price': float(self.product.price) if self.product else 0,
            'image_url': self.product.image_url if self.product else None,
            'stock_quantity': self.product.stock_quantity if self.product else 0
        }

class SupportTicket(db.Model, TimestampMixin):
    """Support ticket model"""
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    
    # Relationships
    responses = db.relationship('TicketResponse', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_ticket_number():
        return 'TKT-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'order_id': self.order_id,
            'ticket_number': self.ticket_number,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'order_number': self.order.order_number if self.order else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TicketResponse(db.Model, TimestampMixin):
    """Ticket response model"""
    __tablename__ = 'ticket_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'responder_id': self.responder_id,
            'message': self.message,
            'responder_name': self.responder.full_name if self.responder else None,
            'responder_role': self.responder.role if self.responder else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
