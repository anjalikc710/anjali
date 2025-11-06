from app import app,db

with app.app_context():
    print("Database tables created successfully!")
