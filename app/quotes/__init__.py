from flask import Blueprint

quote = Blueprint('quote',__name__)

from . import views