from . import main
from flask import render_template

@main.route('/')
def index():
  return render_template('index.html')

@main.route('/help')
def help():
  return render_template('help.html')