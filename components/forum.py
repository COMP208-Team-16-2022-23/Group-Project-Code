from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from components.auth import login_required
from database import db_session
from util.models import Post, Comment, User

bp = Blueprint('forum', __name__, url_prefix='/forum')


@bp.route('/')
def index():
    posts = Post.query.order_by(Post.modified.desc()).all()
    for post in posts:
        post.author = User.query.filter_by(id=post.author_id).first()
        post.comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.modified.desc()).all()
        for comment in post.comments:
            comment.author = User.query.filter_by(id=comment.author_id).first()

    return render_template('forum/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            # Create a new post
            post = Post(author_id=g.user.id, title=title, body=body)
            db_session.add(post)
            db_session.commit()
            return redirect(url_for('forum.index'))

    return render_template('forum/create.html')


def get_post(id, check_author=True):
    post = Post.query.filter_by(id=id).first()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            # Update the post
            post.title = title
            post.body = body
            post.modified = datetime.utcnow()
            db_session.commit()
            return redirect(url_for('forum.index'))

    return render_template('forum/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # Delete the comment
    comment = Comment.query.filter_by(id=id).all()
    if comment:
        db_session.delete(comment)
        db_session.commit()

    post = get_post(id)
    db_session.delete(post)
    db_session.commit()
    return redirect(url_for('forum.index'))
