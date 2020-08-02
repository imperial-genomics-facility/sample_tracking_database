from flask import Blueprint

runs = Blueprint('runs',__name__)

from . import views