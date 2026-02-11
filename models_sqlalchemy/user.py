
from . import db, TimestampMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, TimestampMixin):
    """User model for customers, providers, and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # customer, provider, admin
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    provider_profile = db.relationship('ProviderProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    products = db.relationship('Product', backref='provider_user', lazy='dynamic', foreign_keys='Product.provider_id')
    orders = db.relationship('Order', backref='customer', lazy='dynamic', foreign_keys='Order.customer_id')
    cart_items = db.relationship('CartItem', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    support_tickets = db.relationship('SupportTicket', backref='customer', lazy='dynamic', foreign_keys='SupportTicket.customer_id')
    ticket_responses = db.relationship('TicketResponse', backref='responder', lazy='dynamic', foreign_keys='TicketResponse.responder_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
