from app import app, db
from app.models import User

# The app.py is the root-file, you can run the whole application when executing this file

if __name__ == '__main__':
    app.run(debug=True, port=50051)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

