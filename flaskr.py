# -*- coding: utf-8 -*-
"""
    Flaskr Plus
    ~~~~~~
#Original#
    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()

    if "category" in request.args:
        cur = db.execute('SELECT id, title, category, text FROM entries WHERE category = ? ORDER BY id DESC',
                         [request.args["category"]])
        entries = cur.fetchall()
    else:
        cur = db.execute('SELECT id, title, category, text FROM entries ORDER BY id DESC')
        entries = cur.fetchall()

    cur = db.execute('SELECT DISTINCT category FROM entries ORDER BY category ASC')
    categories = cur.fetchall()

    return render_template('show_entries.html', entries=entries, categories=categories)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT INTO entries (title, category, text) VALUES (?, ?, ?)',
               [request.form['title'], request.form['category'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('DELETE FROM entries WHERE id=?', [request.form['id']])
    db.commit()
    flash('Entry deleted')
    return redirect(url_for('show_entries'))

@app.route('/editpost/<int:id>', methods=['GET', 'POST'])
def editpost(id):
    post = db.session.query(Post).filter(Post.id==id).first()

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['content']

        post.title = title
        post.body = content

        db.session.commit()

        return redirect(url_for('post', id=id))
    else:
        return render_template('something.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
