import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / '.env')

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
    MYSQL_HOST=os.environ.get('MYSQL_HOST', 'localhost'),
    MYSQL_PORT=int(os.environ.get('MYSQL_PORT', '3306')),
    MYSQL_USER=os.environ.get('MYSQL_USER', 'root'),
    MYSQL_PASSWORD=os.environ.get('MYSQL_PASSWORD', ''),
    MYSQL_DATABASE=os.environ.get('MYSQL_DATABASE', 'cinepedia_db'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

bcrypt = Bcrypt(app)

from flask_app.controllers import controlador_usuarios, controlador_peliculas
