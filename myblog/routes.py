from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from myblog import db
from myblog.models import User, Post

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Пользователь уже существует.')
            return redirect(url_for('main.register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна!')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Вы вошли в систему.')
            return redirect(url_for('main.home'))
        else:
            flash('Неверный логин или пароль.')

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли.')
    return redirect(url_for('main.home'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return f'Привет, {current_user.username}! Это защищённая страница.'

@bp.route('/posts')
def post_list():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('post_list.html', posts=posts)

@bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # Проверка на пустые поля
        if not title or not content:
            flash('Заполните все поля.')
            return redirect(url_for('main.create_post'))

        # Создаём новый пост
        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('Пост успешно опубликован!')
        return redirect(url_for('main.post_detail', post_id=post.id))

    return render_template('create_post.html')

@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Проверка: только автор может редактировать
    if post.author != current_user:
        flash('Вы не можете редактировать чужой пост.')
        return redirect(url_for('main.post_detail', post_id=post.id))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title or not content:
            flash('Заполните все поля.')
            return redirect(url_for('main.edit_post', post_id=post.id))

        post.title = title
        post.content = content
        db.session.commit()

        flash('Пост обновлён.')
        return redirect(url_for('main.post_detail', post_id=post.id))

    return render_template('edit_post.html', post=post)

@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Только автор может удалить
    if post.author != current_user:
        flash('Вы не можете удалить чужой пост.')
        return redirect(url_for('main.post_detail', post_id=post.id))

    db.session.delete(post)
    db.session.commit()
    flash('Пост удалён.')
    return redirect(url_for('main.home'))