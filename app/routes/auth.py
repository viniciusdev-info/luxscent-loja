from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Bem-vindo(a), {user.name}! 🎉', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard') if user.is_admin else url_for('shop.home'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not all([name, email, password]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado. Faça login.', 'warning')
            return redirect(url_for('auth.login'))

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Conta criada com sucesso! Bem-vindo(a), {name}! 🎉', 'success')
        return redirect(url_for('shop.home'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('shop.home'))


@auth_bp.route('/minha-conta')
@login_required
def my_account():
    from app.models import Order
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('auth/account.html', orders=orders)
