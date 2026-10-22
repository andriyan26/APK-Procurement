import os
from sqlalchemy import event
from sqlalchemy.engine import Engine
from models import db

# Path file database SQLite di direktori root aplikasi
DB_FILENAME = 'procurement.db'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_FILENAME)

def init_app_db(app):
    """Menginisialisasi konfigurasi database pada aplikasi Flask."""
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # SQLite secara default tidak mengaktifkan PRAGMA foreign_keys = ON.
    # Kita wajib mengaktifkannya agar relasi Foreign Key benar-benar ditegakkan.
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_tables(app):
    """Membuat tabel-tabel sesuai model jika belum ada."""
    with app.app_context():
        db.create_all()
