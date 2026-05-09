from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, default=0)  # Para mostrar desconto
    stock = db.Column(db.Integer, default=0)
    ml = db.Column(db.Integer, default=100)
    gender = db.Column(db.String(20), default='Unissex')
    image = db.Column(db.String(200), default='default.jpg')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_featured = db.Column(db.Boolean, default=False)
    is_bestseller = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    # Notas olfativas
    top_notes = db.Column(db.String(200))
    heart_notes = db.Column(db.String(200))
    base_notes = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='product', lazy='dynamic')

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def is_low_stock(self):
        return self.stock <= 5

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'original_price': self.original_price,
            'discount_percent': self.discount_percent,
            'image': self.image,
            'stock': self.stock,
            'ml': self.ml,
            'gender': self.gender,
            'category': self.category.name if self.category else '',
            'avg_rating': self.avg_rating,
            'review_count': self.review_count,
            'is_low_stock': self.is_low_stock,
        }

    def __repr__(self):
        return f'<Product {self.name}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.reviewer_name} - {self.rating}★>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_whatsapp = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='pendente')  # pendente, confirmado, enviado, entregue
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    STATUS_LABELS = {
        'pendente': ('⏳ Pendente', 'status-pending'),
        'confirmado': ('✅ Confirmado', 'status-confirmed'),
        'enviado': ('🚚 Enviado', 'status-shipped'),
        'entregue': ('📦 Entregue', 'status-delivered'),
        'cancelado': ('❌ Cancelado', 'status-cancelled'),
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, (self.status, ''))[0]

    @property
    def status_class(self):
        return self.STATUS_LABELS.get(self.status, ('', 'status-pending'))[1]

    def __repr__(self):
        return f'<Order #{self.id} - {self.customer_name}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(150), nullable=False)  # Snapshot
    product_price = db.Column(db.Float, nullable=False)  # Snapshot
    quantity = db.Column(db.Integer, nullable=False, default=1)

    @property
    def subtotal(self):
        return self.product_price * self.quantity

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'
