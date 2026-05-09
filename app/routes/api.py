from flask import Blueprint, jsonify, request
from app.models import Product, Category

api_bp = Blueprint('api', __name__)


@api_bp.route('/produtos')
def products():
    """Busca produtos com filtros (para AJAX)."""
    q = request.args.get('q', '')
    category = request.args.get('categoria', '')
    gender = request.args.get('genero', '')

    query = Product.query.filter_by(is_active=True)

    if q:
        query = query.filter(
            Product.name.ilike(f'%{q}%') |
            Product.description.ilike(f'%{q}%')
        )

    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    if gender:
        query = query.filter_by(gender=gender)

    products = query.limit(20).all()
    return jsonify([p.to_dict() for p in products])


@api_bp.route('/produtos/<int:product_id>')
def product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify(p.to_dict())


@api_bp.route('/categorias')
def categories():
    cats = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug} for c in cats])
