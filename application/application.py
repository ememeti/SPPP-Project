from app import app as application 
from app import db
from app.models import User, Group, Item

@application.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'Group': Group, 'Item': Item}
