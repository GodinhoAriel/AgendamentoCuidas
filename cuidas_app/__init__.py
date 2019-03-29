from flask import Flask, g
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_login import LoginManager
import os
import flask_sijax

path = os.path.join('.', os.path.dirname(__file__), 'static\\js\\sijax\\')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fd141cbd0c454da349011c867da4b3db'
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '\\static\\js\\sijax\\json2.js'
flask_sijax.Sijax(app)

#client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.cuidas

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from cuidas_app import routes