from app import app, db
from flask import current_app

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Print table info
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Created tables: {', '.join(tables)}")
            
            # Verify PostgreSQL JSONB support
            result = db.session.execute(db.text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"🐘 PostgreSQL version: {version}")
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            return False
        
        return True

if __name__ == "__main__":
    init_database()