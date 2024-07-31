from flask import Blueprint, render_template

routes = Blueprint("routes", __name__)

@routes.route('/', methods=['GET', 'POST'])
@routes.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@routes.route('/license')
def license():
    return render_template('license.html')
