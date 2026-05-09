from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[config_name])

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Garantir pasta de uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Registrar blueprints
    from app.routes.shop import shop_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(shop_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Criar banco e dados iniciais
    with app.app_context():
        from app import models
        db.create_all()
        _seed_database(app)

    return app


def _seed_database(app):
    """Popula banco com dados de exemplo se estiver vazio."""
    from app.models import User, Product, Category, Review
    from werkzeug.security import generate_password_hash

    # Admin
    if not User.query.filter_by(email=app.config['ADMIN_EMAIL']).first():
        admin = User(
            name='Administrador',
            email=app.config['ADMIN_EMAIL'],
            password=generate_password_hash(app.config['ADMIN_PASSWORD']),
            is_admin=True
        )
        db.session.add(admin)

    # Categorias
    cats = {}
    for name in ['Amadeirado', 'Floral', 'Cítrico', 'Oriental', 'Doce', 'Importado']:
        cat = Category.query.filter_by(name=name).first()
        if not cat:
            cat = Category(name=name, slug=name.lower().replace('á', 'a').replace('í', 'i'))
            db.session.add(cat)
        cats[name] = cat
    db.session.flush()

    # Produtos de exemplo
    if Product.query.count() == 0:
        products_data = [
            {
                'name': 'Black Oud Elixir',
                'price': 189.90,
                'original_price': 249.90,
                'description': 'Uma jornada olfativa pelo Oriente. Notas de oud negro, âmbar e sândalo criam uma sinfonia de elegância e mistério. Perfeito para ocasiões especiais.',
                'category': 'Amadeirado',
                'stock': 15,
                'ml': 100,
                'gender': 'Unissex',
                'is_featured': True,
                'is_bestseller': True,
                'top_notes': 'Bergamota, Limão',
                'heart_notes': 'Rosa, Jasmim',
                'base_notes': 'Oud, Sândalo, Âmbar',
                'image': 'black_oud.jpg'
            },
            {
                'name': 'Golden Rose Intense',
                'price': 159.90,
                'original_price': 199.90,
                'description': 'A essência da feminilidade em cada gota. Rosa bulgara combinada com framboesa e baunilha para uma fragrância irresistível e envolvente.',
                'category': 'Floral',
                'stock': 23,
                'ml': 75,
                'gender': 'Feminino',
                'is_featured': True,
                'is_bestseller': True,
                'top_notes': 'Framboesa, Pêssego',
                'heart_notes': 'Rosa Búlgara, Peônia',
                'base_notes': 'Baunilha, Almíscar, Cedro',
                'image': 'golden_rose.jpg'
            },
            {
                'name': 'Citrus Azzaro Blue',
                'price': 129.90,
                'original_price': 169.90,
                'description': 'Frescor mediterrâneo que dura o dia todo. Limão siciliano, bergamota e notas aquáticas criam uma explosão de energia e vitalidade.',
                'category': 'Cítrico',
                'stock': 31,
                'ml': 100,
                'gender': 'Masculino',
                'is_featured': False,
                'is_bestseller': True,
                'top_notes': 'Limão Siciliano, Bergamota',
                'heart_notes': 'Lavanda, Gerânio',
                'base_notes': 'Cedro, Almíscar Branco',
                'image': 'citrus_blue.jpg'
            },
            {
                'name': 'Velvet Vanilla Dreams',
                'price': 149.90,
                'original_price': 189.90,
                'description': 'Doçura sofisticada que aquece a alma. Baunilha bourbon, caramelo salgado e tonka bean criam uma fragrância viciante e luxuosa.',
                'category': 'Doce',
                'stock': 8,
                'ml': 50,
                'gender': 'Feminino',
                'is_featured': True,
                'is_bestseller': False,
                'top_notes': 'Caramelo, Mel',
                'heart_notes': 'Baunilha Bourbon, Tonka Bean',
                'base_notes': 'Almíscar, Sândalo',
                'image': 'vanilla_dreams.jpg'
            },
            {
                'name': 'Sheikh Al Arab',
                'price': 219.90,
                'original_price': 289.90,
                'description': 'Luxo árabe em sua forma mais pura. Inspirado nas fragâncias do Oriente Médio, com oud precioso, rosa de Taif e especiarias raras.',
                'category': 'Oriental',
                'stock': 12,
                'ml': 100,
                'gender': 'Masculino',
                'is_featured': True,
                'is_bestseller': True,
                'top_notes': 'Açafrão, Cardamomo',
                'heart_notes': 'Rosa de Taif, Oud',
                'base_notes': 'Âmbar, Almíscar, Patchouli',
                'image': 'sheikh_arab.jpg'
            },
            {
                'name': 'Парфюм Noir Suede',
                'price': 249.90,
                'original_price': 0,
                'description': 'Importado da França, este perfume exclusivo combina camurça, violeta e almíscar branco em uma composição única e sofisticada para o homem moderno.',
                'category': 'Importado',
                'stock': 5,
                'ml': 100,
                'gender': 'Masculino',
                'is_featured': True,
                'is_bestseller': False,
                'top_notes': 'Pimenta Rosa, Bergamota',
                'heart_notes': 'Violeta, Camurça',
                'base_notes': 'Almíscar Branco, Sândalo, Cedro',
                'image': 'noir_suede.jpg'
            },
            {
                'name': 'Bloom Floral Chic',
                'price': 119.90,
                'original_price': 149.90,
                'description': 'Leveza e elegância floral para o dia a dia. Jasmim, frésia e neroli compõem uma fragrância fresca e feminina que conquista a todos.',
                'category': 'Floral',
                'stock': 28,
                'ml': 75,
                'gender': 'Feminino',
                'is_featured': False,
                'is_bestseller': True,
                'top_notes': 'Neroli, Bergamota',
                'heart_notes': 'Jasmim, Frésia, Peônia',
                'base_notes': 'Almíscar, Cedro, Âmbar Branco',
                'image': 'bloom_floral.jpg'
            },
            {
                'name': 'Intense Leather Oud',
                'price': 179.90,
                'original_price': 229.90,
                'description': 'Para o homem que não passa despercebido. Couro italiano, oud defumado e especiarias quentes criam uma assinatura olfativa inesquecível.',
                'category': 'Amadeirado',
                'stock': 19,
                'ml': 100,
                'gender': 'Masculino',
                'is_featured': False,
                'is_bestseller': False,
                'top_notes': 'Pimenta Preta, Gengibre',
                'heart_notes': 'Couro, Oud',
                'base_notes': 'Sândalo, Vetiver, Âmbar',
                'image': 'leather_oud.jpg'
            },
        ]

        for pd in products_data:
            cat = Category.query.filter_by(name=pd['category']).first()
            p = Product(
                name=pd['name'],
                price=pd['price'],
                original_price=pd.get('original_price', 0),
                description=pd['description'],
                category_id=cat.id if cat else None,
                stock=pd['stock'],
                ml=pd['ml'],
                gender=pd['gender'],
                is_featured=pd['is_featured'],
                is_bestseller=pd['is_bestseller'],
                top_notes=pd['top_notes'],
                heart_notes=pd['heart_notes'],
                base_notes=pd['base_notes'],
                image=pd['image']
            )
            db.session.add(p)

        db.session.flush()

        # Reviews de exemplo
        reviews_data = [
            (1, 'Maria Silva', 5, 'Perfume incrível! Dura o dia inteiro e recebo muitos elogios. Super recomendo!'),
            (1, 'João Santos', 5, 'Melhor perfume que já comprei. Vale muito o investimento!'),
            (2, 'Ana Costa', 5, 'Delicioso e feminino. Minha fragrância favorita agora!'),
            (3, 'Pedro Lima', 4, 'Ótimo perfume masculino. Muito refrescante para o verão.'),
            (5, 'Carlos Oliveira', 5, 'Exótico e marcante. Qualidade árabe autêntica!'),
        ]
        for pid, name, rating, comment in reviews_data:
            r = Review(
                product_id=pid,
                reviewer_name=name,
                rating=rating,
                comment=comment
            )
            db.session.add(r)

    db.session.commit()
