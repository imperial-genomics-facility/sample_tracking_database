from . import main
from flask import render_template

@main.app_errorhandler(404)
def error_404(e):
	return render_template('404.html'),404

@main.app_errorhandler(500)
def error_500(e):
	return render_template('500.html'),500