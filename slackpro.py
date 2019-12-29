from app.models import UserTable
from app import db
from app import app

@app.shell_context_processor
def shell_context_processor():
    return {'db': db}
