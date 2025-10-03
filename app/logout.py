from app import app
from flask import make_response, redirect, url_for
from app.cookie import logout_cookie

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    logout_cookie(response)
    return response
