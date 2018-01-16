from app import app
from db import db

db.init_app(app)

@app.before_first_request
def create_tables():
    # This creates the database at the app.config location set above
    db.create_all()