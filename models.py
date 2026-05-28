from datetime import datetime, timezone
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def get_utc_now():
    """Generates a timezone-naive UTC datetime suitable for DB columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Extended length for secure werkzeug hashes
    role = db.Column(db.String(20), default='Buyer', nullable=False)  # 'Buyer', 'Seller', 'Admin'
    balance = db.Column(db.Float, default=0.0, nullable=False)
    two_factor_enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    products = db.relationship('Product', backref='seller', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='buyer', lazy=True)

    def set_password(self, password):
        """Hashes password securely using modern salted password hashes."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies password using secure comparison."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'balance': self.balance,
            'two_factor_enabled': self.two_factor_enabled,
            'created_at': self.created_at.isoformat()
        }


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=1)
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True, default='{}')  # Dynamic custom product attributes
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def get_metadata(self):
        """Safely retrieves metadata_json as a Python dictionary."""
        if not self.metadata_json:
            return {}
        try:
            return json.loads(self.metadata_json)
        except Exception:
            return {}

    def set_metadata(self, data):
        """Safely saves a dictionary to metadata_json."""
        self.metadata_json = json.dumps(data)

    def to_dict(self):
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'stock': self.stock,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'metadata': self.get_metadata()
        }


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), default='Cart', nullable=False)  # 'Cart', 'Paid/Pending', 'Shipped', 'Completed', 'Cancelled'
    payment_proof_path = db.Column(db.String(500), nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'total_price': self.total_price,
            'status': self.status,
            'payment_proof_path': self.payment_proof_path,
            'shipping_address': self.shipping_address,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase
        }


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # 'AUTH', 'ORDER', 'USER', 'CSV_IMPORT', 'SYSTEM'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }


class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)  # 1 to 5 stars
    comment = db.Column(db.Text, nullable=False)
    seller_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='reviews', lazy=True)
    product = db.relationship('Product', backref='reviews', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else "Пользователь",
            'rating': self.rating,
            'comment': self.comment,
            'seller_reply': self.seller_reply,
            'created_at': self.created_at.isoformat()
        }


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True) # None for group channels
    room_id = db.Column(db.String(100), nullable=False, index=True) # e.g. "lobby", "support_12", "dm_12_34"
    message = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500), nullable=True) # optional attachments
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages', lazy=True)
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.full_name if self.sender else "Deleted User",
            'sender_role': self.sender.role if self.sender else "Buyer",
            'receiver_id': self.receiver_id,
            'receiver_name': self.receiver.full_name if self.receiver else None,
            'room_id': self.room_id,
            'message': self.message,
            'attachment_url': self.attachment_url,
            'created_at': self.created_at.isoformat()
        }


class InterestGroup(db.Model):
    __tablename__ = 'interest_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False) # e.g. "group_1"
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    
    created_by = db.relationship('User', backref='created_groups', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'created_by_id': self.created_by_id,
            'created_by_name': self.created_by.full_name if self.created_by else "System",
            'created_at': self.created_at.isoformat()
        }
