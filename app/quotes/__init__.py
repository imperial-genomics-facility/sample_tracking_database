from flask import Blueprint

quotes = Blueprint('quotes',__name__)

from . import views