from app import app
from flask import Flask, render_template, flash, redirect, url_for
from app.forms import LoginForm

@app.route("/")
@app.route("/index")
def home_site():
    user = {'username': 'Andi'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route("/overview")
def overview():
    user = {'username': 'Voestalpine'}
    posts = [
        {
            'author': {'username': 'Employee-number'},
            'body': '2435'
        },
        {
            'author': {'username': 'Securities for Sale'},
            'body': '19123 á 16€'
        }
    ]
    return render_template('index.html', title='Overview', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('home_site'))
    return render_template('login.html', title='Sign In', form=form)