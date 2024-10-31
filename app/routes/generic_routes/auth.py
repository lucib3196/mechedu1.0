from typing import Never
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user,login_required,logout_user

from ...form.forms import LoginForm,SignUp
from ...db_models.models import User, db

auth = Blueprint("auth", __name__)

@auth.route('/login', methods = ["GET", "POST"] )
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,remember=form.remember_me.data)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("routes.home")
            return redirect(next)
        else:
            flash('Invalid username or password.',category='error')
    return render_template("login.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignUp()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            password=form.password.data  # Password will be hashed in the model
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('You can now login.')
        return redirect(url_for('routes.home'))
    return render_template("signup.html", form=form)