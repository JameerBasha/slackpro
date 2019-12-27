from app.models import UserTable
from app import create_app,db


@app.shell_context_processor
def shell_context_processor():
    return {'db': db}
