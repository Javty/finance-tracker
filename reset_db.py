import os
from app import db, app

db_path = os.path.join(os.path.dirname(__file__), 'finance.db')

if os.path.exists(db_path):
    os.remove(db_path)
    print("✅ Base de datos eliminada.")

with app.app_context():
    db.create_all()
    print("✅ Base de datos creada nuevamente.")