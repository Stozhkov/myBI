from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from celery import Celery


app = Flask(__name__)
app.config.from_object(Configuration)

celery = Celery('tasks', backend='rpc://', broker='amqp://')

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from models import *

