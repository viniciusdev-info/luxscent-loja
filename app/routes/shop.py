from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, jsonify
from app.models import Product, Category, Order, OrderItem, Review
from app import db
import urllib.parse

shop_bp = Blueprint('shop', __name__)


def get_cart():
    return session.get('cart', {})


def save_cart(cart):
    session['cart'] = cart
    session.modified = True


def cart_total(cart):
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return round(total, 2)


def cart_count(cart):
    return sum(item['quantity'] for item in cart.values())


@shop_bp.context_processor
def inject_cart():
    cart = get_cart()
    return {'cart_count': cart_count(cart), 'cart_total': cart_total(cart)}


# ─── HOME ───────────────────────────────────────────────────────────────────

@shop_bp.route('/')
def home():
    featured = Product.query.filter_by(is_featured=True, is_active=True).limit(6).all()
    bestsellers = Product.query.filter_by(is_bestseller=True, is_active=True).limit(4).all()
    categories = Category.query.all()
    return render_template('shop/home.html',
                           featured=featured,
                           bestsellers=bestsellers,
                           categories=categories)


# ─── CATÁLOGO ───────────────────────────────────────────────────────────────

@shop_bp.route('/catalogo')
def catalog():
    query = request.args.get('q', '')
    category_slug = request.args.get('categoria', '')
    gender = request.args.get('genero', '')
    sort = request.args.get('ordenar', 'nome')

    products_query = Product.query.filter_by(is_active=True)

    if query:
        products_query = products_query.filter(
            Product.name.ilike(f'%{query}%') |
            Product.description.ilike(f'%{query}%')
        )

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            products_query = products_query.filter_by(category_id=cat.id)

    if gender:
        products_query = products_query.filter_by(gender=gender)

    if sort == 'preco_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort == 'preco_desc':
        products_query = products_query.order_by(Product.price.desc())
    elif sort == 'novos':
        products_query = products_query.order_by(Product.created_at.desc())
    else:
        products_query = products_query.order_by(Product.name.asc())

    products = products_query.all()
    categories = Category.query.all()

    return render_template('shop/catalog.html',
                           products=products,
                           categories=categories,
                           selected_cat=category_slug,
                           selected_gender=gender,
                           selected_sort=sort,
                           query=query)


# ─── PRODUTO ────────────────────────────────────────────────────────────────

@shop_bp.route('/produto/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = product.reviews.order_by(Review.created_at.desc()).all()
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    return render_template('shop/product.html', product=product, reviews=reviews, related=related)


# ─── AVALIAÇÃO ──────────────────────────────────────────────────────────────

@shop_bp.route('/produto/<int:product_id>/avaliar', methods=['POST'])
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    name = request.form.get('name', '').strip()
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '').strip()

    if name and comment and 1 <= rating <= 5:
        review = Review(
            product_id=product.id,
            reviewer_name=name,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        flash('Avaliação enviada com sucesso! Obrigado!', 'success')
    else:
        flash('Por favor, preencha todos os campos da avaliação.', 'danger')

    return redirect(url_for('shop.product_detail', product_id=product_id))


# ─── CARRINHO ───────────────────────────────────────────────────────────────

@shop_bp.route('/carrinho')
def cart():
    cart = get_cart()
    items = []
    for pid, item in cart.items():
        items.append({
            'id': pid,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'image': item.get('image', 'default.jpg'),
            'subtotal': round(item['price'] * item['quantity'], 2)
        })
    total = cart_total(cart)
    return render_template('shop/cart.html', items=items, total=total)


@shop_bp.route('/carrinho/adicionar/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        cart[pid]['quantity'] = min(cart[pid]['quantity'] + quantity, product.stock)
    else:
        cart[pid] = {
            'name': product.name,
            'price': product.price,
            'quantity': min(quantity, product.stock),
            'image': product.image
        }

    save_cart(cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'cart_count': cart_count(cart),
            'cart_total': cart_total(cart),
            'message': f'{product.name} adicionado ao carrinho!'
        })

    flash(f'✅ {product.name} adicionado ao carrinho!', 'success')
    return redirect(request.referrer or url_for('shop.catalog'))


@shop_bp.route('/carrinho/remover/<string:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(product_id, None)
    save_cart(cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'cart_count': cart_count(cart), 'cart_total': cart_total(cart)})

    flash('Item removido do carrinho.', 'info')
    return redirect(url_for('shop.cart'))


@shop_bp.route('/carrinho/atualizar', methods=['POST'])
def update_cart():
    cart = get_cart()
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if product_id in cart:
        if quantity <= 0:
            cart.pop(product_id)
        else:
            product = Product.query.get(int(product_id))
            max_qty = product.stock if product else 99
            cart[product_id]['quantity'] = min(quantity, max_qty)

    save_cart(cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        item = cart.get(product_id, {})
        subtotal = round(item.get('price', 0) * item.get('quantity', 0), 2) if item else 0
        return jsonify({
            'success': True,
            'cart_count': cart_count(cart),
            'cart_total': cart_total(cart),
            'item_subtotal': subtotal
        })

    return redirect(url_for('shop.cart'))


# ─── CHECKOUT ───────────────────────────────────────────────────────────────

@shop_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = get_cart()
    if not cart:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('shop.catalog'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        address = request.form.get('address', '').strip()

        if not all([name, whatsapp, address]):
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('shop.checkout'))

        total = cart_total(cart)

        # Salvar pedido no banco
        order = Order(
            customer_name=name,
            customer_whatsapp=whatsapp,
            customer_address=address,
            total=total,
            status='pendente'
        )
        db.session.add(order)
        db.session.flush()

        items_lines = []
        for pid, item in cart.items():
            oi = OrderItem(
                order_id=order.id,
                product_id=int(pid),
                product_name=item['name'],
                product_price=item['price'],
                quantity=item['quantity']
            )
            db.session.add(oi)
            items_lines.append(f"• {item['name']} ({item['quantity']}x) - R$ {item['price']:.2f}")

        db.session.commit()

        # Gerar link WhatsApp
        wa_number = current_app.config['WHATSAPP_NUMBER']
        items_text = '\n'.join(items_lines)
        message = (
            f"Olá! Quero fazer um pedido 🛍️\n\n"
            f"*Nome:* {name}\n"
            f"*WhatsApp:* {whatsapp}\n"
            f"*Endereço:* {address}\n\n"
            f"*Produtos:*\n{items_text}\n\n"
            f"*Total: R$ {total:.2f}*\n\n"
            f"Pedido #{order.id} - Aguardo confirmação!"
        )
        wa_url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(message)}"

        # Limpar carrinho
        session.pop('cart', None)

        return redirect(url_for('shop.order_success', order_id=order.id, wa_url=urllib.parse.quote(wa_url)))

    items = []
    for pid, item in cart.items():
        items.append({
            'id': pid,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'image': item.get('image', 'default.jpg'),
            'subtotal': round(item['price'] * item['quantity'], 2)
        })

    return render_template('shop/checkout.html', items=items, total=cart_total(cart))


@shop_bp.route('/pedido-confirmado/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    wa_url = urllib.parse.unquote(request.args.get('wa_url', ''))
    return render_template('shop/order_success.html', order=order, wa_url=wa_url)
