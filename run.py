"""
LuxScent — Ponto de entrada da aplicação.
Execute: python run.py
"""
import os
from app import create_app

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    print("=" * 55)
    print("  ✦  LuxScent — E-commerce de Perfumes")
    print("  🌐  http://localhost:5000")
    print("  🔐  Admin: http://localhost:5000/admin")
    print("  📧  admin@luxscent.com  |  Senha: Admin@123")
    print("=" * 55)
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(config_name == 'development')
    )
