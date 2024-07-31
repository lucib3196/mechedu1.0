from flask import Blueprint, render_template

routes = Blueprint("route",__name__)
@routes.route('/', methods=['GET', 'POST'])
@routes.route('/home', methods=['GET', 'POST'])


def home():
    return render_template("home.html")