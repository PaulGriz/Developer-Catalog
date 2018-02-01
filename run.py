from app import app, db
from app.models import User, Category, Item


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Category': Category, 'Item': Item}


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
