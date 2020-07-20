from . import main
from flask import request

@main.app_context_processor
def inject_template_scope():
  injections = dict()

  def cookies_check():
    value = request.cookies.get('cookie_consent')
    return value == 'true'
  injections.update(cookies_check=cookies_check)
  return injections