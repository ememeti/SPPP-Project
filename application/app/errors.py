from flask import render_template
from app import app, db

@app.errorhandler(404)
def page_not_found_error(error) :
  return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error) :
  db.session.rollback()
  return render_template('500.html'), 500


@app.errorhandler(505)
def html_version_not_supported_error(error) :
  return render_template('505.html'), 505


@app.errorhandler(413)
def file_size_too_big_error(error) :
  return render_template('413.html'), 413


@app.errorhandler(429)
def request_exceed_error(error) :
  return render_template('429.html'), 429
