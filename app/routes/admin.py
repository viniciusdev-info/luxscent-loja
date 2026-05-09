from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app.models import Product, Category, Order, User, Review
from app import db
import os
import uuid

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Área restrita.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file):
    """Salva imagem e retorna o nome do arquivo."""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return filename
    return None


# ─── DASHBOARD ──────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock = Product.query.filter(Product.stock <= 5, Product.is_active == True).all()

    # Pedidos por status
    status_counts = {}
    for status in ['pendente', 'confirmado', 'enviado', 'entregue']:
        status_counts[status] = Order.query.filter_by(status=status).count()

    return render_template('admin/dashboard.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           total_users=total_users,
                           revenue=revenue,
                           recent_orders=recent_orders,
                           low_stock=low_stock,
                           status_counts=status_counts)


# ─── PRODUTOS ───────────────────────────────────────────────────────────────

@admin_bp.route('/produtos')
@login_required
@admin_required
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def product_new():
    categories = Category.query.all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', 0))
        original_price = float(request.form.get('original_price', 0))
        stock = int(request.form.get('stock', 0))
        ml = int(request.form.get('ml', 100))
        gender = request.form.get('gender', 'Unissex')
        category_id = request.form.get('category_id')
        is_featured = request.form.get('is_featured') == 'on'
        is_bestseller = request.form.get('is_bestseller') == 'on'
        top_notes = request.form.get('top_notes', '').strip()
        heart_notes = request.form.get('heart_notes', '').strip()
        base_notes = request.form.get('base_notes', '').strip()

        image_file = request.files.get('image')
        image_name = save_image(image_file) or 'default.jpg'

        product = Product(
            name=name, description=description, price=price,
            original_price=original_price, stock=stock, ml=ml,
            gender=gender, category_id=int(category_id) if category_id else None,
            is_featured=is_featured, is_bestseller=is_bestseller,
            top_notes=top_notes, heart_notes=heart_notes, base_notes=base_notes,
            image=image_name
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Produto "{name}" criado com sucesso!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', product=None, categories=categories)


@admin_bp.route('/produtos/editar/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.description = request.form.get('description', '').strip()
        product.price = float(request.form.get('price', 0))
        product.original_price = float(request.form.get('original_price', 0))
        product.stock = int(request.form.get('stock', 0))
        product.ml = int(request.form.get('ml', 100))
        product.gender = request.form.get('gender', 'Unissex')
        cat_id = request.form.get('category_id')
        product.category_id = int(cat_id) if cat_id else None
        product.is_featured = request.form.get('is_featured') == 'on'
        product.is_bestseller = request.form.get('is_bestseller') == 'on'
        product.is_active = request.form.get('is_active') == 'on'
        product.top_notes = request.form.get('top_notes', '').strip()
        product.heart_notes = request.form.get('heart_notes', '').strip()
        product.base_notes = request.form.get('base_notes', '').strip()

        image_file = request.files.get('image')
        new_image = save_image(image_file)
        if new_image:
            product.image = new_image

        db.session.commit()
        flash(f'Produto "{product.name}" atualizado!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', product=product, categories=categories)


@admin_bp.route('/produtos/deletar/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False  # Soft delete
    db.session.commit()
    flash(f'Produto "{product.name}" desativado.', 'warning')
    return redirect(url_for('admin.products'))


# ─── PEDIDOS ────────────────────────────────────────────────────────────────

@admin_bp.route('/pedidos')
@login_required
@admin_required
def orders():
    status_filter = request.args.get('status', '')
    q = Order.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    orders = q.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@admin_bp.route('/pedidos/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/pedidos/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def order_update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    valid = ['pendente', 'confirmado', 'enviado', 'entregue', 'cancelado']
    if new_status in valid:
        order.status = new_status
        db.session.commit()
        flash(f'Status atualizado para: {new_status}', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))


# ─── CATEGORIAS ─────────────────────────────────────────────────────────────

@admin_bp.route('/categorias')
@login_required
@admin_required
def categories():
    cats = Category.query.all()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/categorias/nova', methods=['POST'])
@login_required
@admin_required
def category_new():
    name = request.form.get('name', '').strip()
    if name:
        slug = name.lower().replace(' ', '-')
        for ch, rep in [('á','a'),('à','a'),('ã','a'),('â','a'),('é','e'),('ê','e'),('í','i'),('ó','o'),('ô','o'),('õ','o'),('ú','u'),('ç','c')]:
            slug = slug.replace(ch, rep)
        if not Category.query.filter_by(slug=slug).first():
            cat = Category(name=name, slug=slug)
            db.session.add(cat)
            db.session.commit()
            flash(f'Categoria "{name}" criada!', 'success')
        else:
            flash('Categoria já existe.', 'warning')
    return redirect(url_for('admin.categories'))
